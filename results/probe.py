#!/usr/bin/env python3
"""Frozen-feature probe heads: fit one on a train split, apply it to any feature store.

    python results/probe.py fit   --spec probes/arcface.json --features SRC_STORE \
                                  --manifest m.parquet --out probe.npz
    python results/probe.py apply --probe probe.npz --features STORE --cache CACHE_BASE

``reidbench`` scores systems and does not train them — its ``pyproject.toml`` says so where
a ``probe`` extra would otherwise go — so the two hundred lines that optimise a head live
here, in the experiment repo, and hand their output back as a value the library already
understands: a content-addressed feature store, readable by ``reidbench score --features``.

**A head is part of the encoder's identity, not a separate stage.** The package already
treats an adaptor that way: two output heads of one checkpoint produce two embeddings and
must not share a cache key. A trained head is the same thing, so ``apply`` writes a store
whose encoder description is the frozen encoder's *with a ``head`` node inside it*. The key
is then the digest of that composite, the weight digests are in it, and a re-fit with a
different seed addresses a different directory without anyone maintaining a naming scheme.

Every head reduces to one affine map on the L2-normalised frozen feature::

    e = W (x / ||x||) + b

which is all ``apply`` has to know. What ``fit`` did to arrive at ``W`` — a supervised
classifier, an angular-margin classifier, or an unsupervised rotation — is in the
description and nowhere in the arithmetic that follows.

Python 3.11+; numpy and pyarrow always, torch only for the supervised heads.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent

_src = PROJECT / "reidbench" / "src"
if _src.is_dir():  # the sibling checkout, so a fresh clone works without an install step
    sys.path.insert(0, str(_src))

from reidbench import cache, manifest as manifest_mod  # noqa: E402
from reidbench.describe import digest, env, now, timing  # noqa: E402
from reidbench.encode import describe as describe_encoder  # noqa: E402  — data only, no torch
from reidbench.transform import align  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CHUNK = 8192
"""Rows projected at a time. A store is memory-mapped fp16 and can be a gigabyte."""


# ------------------------------------------------------------------------------ the maths


def normalise(X: np.ndarray) -> np.ndarray:
    """L2-normalise rows, in float32. Every head's input, so no head can forget it.

    The frozen feature's *norm* is a property of the image — its resolution, its contrast —
    and not of the identity in it, and cosine scoring downstream discards that norm anyway.
    Normalising before the head rather than after it means the head is fitted on the same
    quantity the retrieval metric will read.
    """
    X = np.asarray(X, dtype=np.float32)
    return X / np.maximum(np.linalg.norm(X, axis=1, keepdims=True), 1e-12)


def project(X: np.ndarray, W: np.ndarray, b: np.ndarray, chunk: int = CHUNK) -> np.ndarray:
    """``e = W (x/||x||) + b`` over a whole store, in blocks."""
    out = np.empty((X.shape[0], W.shape[0]), dtype=np.float32)
    for start in range(0, X.shape[0], chunk):
        stop = start + chunk
        out[start:stop] = normalise(X[start:stop]) @ W.T + b
    return out


def fit_pca(spec: dict[str, Any], Z: np.ndarray, y: np.ndarray, n_classes: int) -> Any:
    """The control, and the reason the other two are readable.

    A supervised head that beats the frozen encoder may have learned identity structure, or
    it may only have reduced 2560 dimensions to 512. PCA over the *same* train split, using
    none of the labels, separates the two: whatever it gains is the bottleneck alone.
    """
    mean = Z.mean(axis=0)
    _, singular, components = np.linalg.svd(Z - mean, full_matrices=False)
    W = components[: spec["dim"]]
    explained = float((singular[: spec["dim"]] ** 2).sum() / (singular**2).sum())
    return W, -(W @ mean), {"explained_variance_ratio": round(explained, 4)}


def fit_torch(spec: dict[str, Any], Z: np.ndarray, y: np.ndarray, n_classes: int) -> Any:
    """``linear`` and ``arcface``: one reduction layer, two ways of pushing on it.

    Both train a ``D -> dim`` layer whose output *is* the retrieval embedding, followed by a
    classifier over the train split's identities that exists only to supply a gradient and
    is discarded here. They differ in that classifier: a plain linear layer under
    cross-entropy, versus an angular-margin one that optimises the cosine geometry the
    retrieval metric actually reads.

    No P×K sampler. The protocol asks for one to match a sibling study, but P×K exists to
    populate a batch with mineable positive pairs and neither loss here mines pairs; with
    cross-entropy over identity classes a shuffled batch is the standard and simpler thing.
    """
    import torch
    from torch import nn
    from torch.nn import functional as F

    device = _device(torch)
    torch.manual_seed(spec["seed"])
    X = torch.from_numpy(Z).to(device)
    Y = torch.from_numpy(y.astype(np.int64)).to(device)

    reduce = nn.Linear(X.shape[1], spec["dim"]).to(device)
    classifier = (
        arcface(spec["dim"], n_classes, spec["scale"], spec["margin"]).to(device)
        if spec["head"] == "arcface"
        else nn.Linear(spec["dim"], n_classes).to(device)
    )
    smoothing = spec.get("label_smoothing", 0.0) if spec["head"] == "linear" else 0.0
    optimiser = torch.optim.AdamW(
        [*reduce.parameters(), *classifier.parameters()],
        lr=spec["lr"],
        weight_decay=spec["weight_decay"],
    )
    per_epoch = math.ceil(len(Y) / spec["batch_size"])
    schedule = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimiser, T_max=spec["epochs"] * per_epoch
    )

    generator = torch.Generator(device="cpu").manual_seed(spec["seed"])
    history = []
    for epoch in range(spec["epochs"]):
        order = torch.randperm(len(Y), generator=generator).to(device)
        total, correct, loss_sum = 0, 0, 0.0
        for start in range(0, len(order), spec["batch_size"]):
            rows = order[start : start + spec["batch_size"]]
            embedding = reduce(X[rows])
            logits = (
                classifier(embedding, Y[rows])
                if spec["head"] == "arcface"
                else classifier(embedding)
            )
            loss = F.cross_entropy(logits, Y[rows], label_smoothing=smoothing)
            optimiser.zero_grad(set_to_none=True)
            loss.backward()
            optimiser.step()
            schedule.step()
            total += len(rows)
            correct += int((logits.argmax(1) == Y[rows]).sum())
            loss_sum += float(loss) * len(rows)
        loss_mean, top1 = round(loss_sum / total, 4), round(correct / total, 4)
        history.append({"epoch": epoch, "loss": loss_mean, "top1": top1})
        print(f"    epoch {epoch + 1:3}/{spec['epochs']}  loss {loss_mean:.4f}  top1 {top1:.4f}")

    W = reduce.weight.detach().cpu().numpy().astype(np.float32)
    b = reduce.bias.detach().cpu().numpy().astype(np.float32)
    return W, b, {"device": device, "epochs": history, "train_top1": history[-1]["top1"]}


def arcface(dim: int, n_classes: int, scale: float, margin: float) -> Any:
    """Additive angular margin, in the acos form. Torch is imported where it is used.

    ``cos(theta + m)`` stops being a margin once ``theta + m`` passes pi — it turns back
    upwards and rewards the worst examples. The reference implementation patches that with
    a threshold and an offset; clamping the angle at pi is the same fix said once, and it
    keeps the head three lines long.
    """
    import torch
    from torch import nn
    from torch.nn import functional as F

    class ArcFace(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.weight = nn.Parameter(torch.empty(n_classes, dim))
            nn.init.xavier_uniform_(self.weight)

        def forward(self, embedding: Any, target: Any) -> Any:
            cosine = F.normalize(embedding) @ F.normalize(self.weight).T
            theta = torch.acos(cosine.clamp(-1 + 1e-7, 1 - 1e-7))
            margined = torch.cos((theta + margin).clamp(max=math.pi))
            hit = F.one_hot(target, n_classes).bool()
            return scale * torch.where(hit, margined, cosine)

    return ArcFace()


HEADS = {"pca": fit_pca, "linear": fit_torch, "arcface": fit_torch}


def _device(torch: Any) -> str:
    wanted = os.environ.get("REIDBENCH_DEVICE", "cuda")
    return wanted if wanted != "cuda" or torch.cuda.is_available() else "cpu"


# ------------------------------------------------------------------------------- the file
#
# A fitted probe is a value on disk: two arrays and the description of everything that
# produced them. It is fitted once and applied to every target dataset, which is the whole
# reason `fit` and `apply` are separate verbs rather than one flag.


def write_probe(path: Path, W: np.ndarray, b: np.ndarray, description: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, W=W, b=b, description=json.dumps(description, sort_keys=True))
    return path


def read_probe(path: Path) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    blob = np.load(path, allow_pickle=False)
    return blob["W"], blob["b"], json.loads(str(blob["description"]))


def head_node(spec: dict[str, Any], name: str, W: np.ndarray, b: np.ndarray,
              encoder: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    """The head's node in the description tree — everything that changes the embedding.

    It is hashed into the cache key of every store this head produces, so a re-fit at a
    different seed, a different dimension or over a different train split addresses a
    different directory without anyone naming one. ``weights`` is the two arrays' content
    digests, which is what makes that true of *any* difference, including one nobody
    anticipated putting in the spec.

    ``encoder_digest`` is the frozen encoder this head was fitted on. The node sits inside
    that same encoder's description when it is applied in-domain, where it is redundant —
    and does not when the head is carried to another dataset, which is exactly the case
    where a reader needs to know which features it learned to read.
    """
    return {
        "kind": "head",
        "id": name,
        **{k: v for k, v in spec.items() if k != "train"},
        "input_norm": "l2",
        "source": source,
        "encoder_digest": digest(encoder),
        "weights": {"W": _array(W), "b": _array(b)},
    }


def _array(x: np.ndarray) -> dict[str, Any]:
    from reidbench.describe import describe

    return describe(np.asarray(x))


# ---------------------------------------------------------------------------------- verbs


def cmd_fit(args: argparse.Namespace) -> int:
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    name = spec.get("name") or args.spec.stem
    if spec["head"] not in HEADS:
        raise SystemExit(f"unknown head {spec['head']!r}; known: {sorted(HEADS)}")

    uids, X, description = cache.read_path(args.features)
    table = manifest_mod.read(args.manifest)
    stored_digest = (description.get("manifest") or {}).get("digest")
    if stored_digest and stored_digest != manifest_mod.content_digest(table):
        raise SystemExit(
            f"{args.manifest} is not the table {args.features} was extracted over "
            f"(digest {manifest_mod.content_digest(table)} vs {stored_digest}); "
            "the labels would be joined onto features of a different dataset state"
        )

    split = spec["train"]["split"]
    cols = manifest_mod.columns(table, ["uid", "pid", "split"])
    keep = (cols["split"] == split) & (cols["pid"] >= 0)
    if not keep.any():
        raise SystemExit(f"no labelled rows in split {split!r}; nothing to fit")
    identities, y = np.unique(cols["pid"][keep], return_inverse=True)
    Z = normalise(align(uids, X, cols["uid"][keep]))
    source = {
        "dataset": description.get("dataset"),
        "split": split,
        "manifest_digest": stored_digest,
        "n_images": int(Z.shape[0]),
        "n_identities": int(identities.size),
    }
    print(
        f"[  fit ] {name} on {source['dataset']}/{split} — "
        f"{source['n_images']} images, {source['n_identities']} identities, {Z.shape[1]}d"
    )

    started = time.perf_counter()
    W, b, training = HEADS[spec["head"]](spec, Z, y, int(identities.size))
    elapsed = time.perf_counter() - started

    encoder = description["encoder"]
    node = head_node(spec, name, W, b, encoder, source)
    written = write_probe(
        args.out,
        W,
        b,
        {
            "kind": "probe",
            "head": node,
            "encoder": encoder,
            "training": {**training, **timing(source["n_images"] * spec.get("epochs", 1), elapsed)},
            "fitted_at": now(),
            "env": env(),
        },
    )
    print(f"wrote {written} — W {W.shape}, {elapsed:.1f}s")
    return 0


def cmd_apply(args: argparse.Namespace) -> int:
    W, b, probe = read_probe(args.probe)
    node = probe["head"]
    uids, X, description = cache.read_path(args.features)
    encoder = description["encoder"]
    if digest(encoder) != node["encoder_digest"]:
        raise SystemExit(
            f"{args.probe} was fitted on {probe['encoder'].get('id')} "
            f"{probe['encoder'].get('input_size')} and {args.features} holds "
            f"{encoder.get('id')} {encoder.get('input_size')}; a head is a map out of one "
            "feature space and means nothing applied to another"
        )

    dataset = description.get("dataset", "unknown")
    composite = {**encoder, "head": node}
    key = cache.key(composite, description["manifest"]["digest"], args.storage_dtype)
    if cache.exists(key, dataset, args.cache):
        print(f"cache hit {key}; nothing to do")
        return 0

    started = time.perf_counter()
    E = project(X, W, b)
    elapsed = time.perf_counter() - started
    directory = cache.write(
        key,
        uids,
        E,
        {
            "encoder": composite,
            "manifest": description["manifest"],
            "probe_training": probe["training"],
        },
        dataset=dataset,
        base=args.cache,
        storage_dtype=args.storage_dtype,
        timing=timing(E.shape[0], elapsed, source_key=description.get("key")),
    )
    print(f"wrote {directory} — {E.shape}, {node['id']} over {dataset}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    fit = sub.add_parser("fit", help="train a head on one store's train split")
    fit.add_argument("--spec", type=Path, required=True, help="a probe spec, JSON")
    fit.add_argument("--features", type=Path, required=True, help="the source feature store")
    fit.add_argument("--manifest", type=Path, required=True, help="that store's manifest")
    fit.add_argument("--out", type=Path, required=True, help="destination .npz")

    apply_ = sub.add_parser("apply", help="project a store through a fitted head")
    apply_.add_argument("--probe", type=Path, required=True, help="an .npz written by `fit`")
    apply_.add_argument("--features", type=Path, required=True, help="the store to project")
    apply_.add_argument("--cache", type=Path, required=True, help="cache base to write into")
    apply_.add_argument("--storage-dtype", default="float16")

    args = parser.parse_args(argv)
    return {"fit": cmd_fit, "apply": cmd_apply}[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
