# Datasets

## market1501

| # | encoder                                 | resolution | protocol              | mAP    | R1     | R5     | R10    | mINP   |
|---|-----------------------------------------|------------|-----------------------|--------|--------|--------|--------|--------|
| 1 | timm:vit_base_patch16_clip_224.openai   | 224x224    | market1501/official@1 | 0.0227 | 0.0879 | 0.1829 | 0.2381 | 0.0015 |
| 2 | torchhub:NVlabs/RADIO/c-radio_v4-h      | 224x224    | market1501/official@1 | 0.0610 | 0.1838 | 0.3207 | 0.3955 | 0.0044 |
| 3 | torchhub:NVlabs/RADIO/c-radio_v4-h      | 256x128    | market1501/official@1 | 0.0592 | 0.1799 | 0.3224 | 0.3955 | 0.0052 |
| 4 | torchhub:NVlabs/RADIO/c-radio_v4-h      | native     | market1501/official@1 | 0.0443 | 0.1393 | 0.2672 | 0.3305 | 0.0044 |
| 5 | torchhub:NVlabs/RADIO/c-radio_v4-so400m | 224x224    | market1501/official@1 | 0.0628 | 0.1832 | 0.3180 | 0.3869 | 0.0055 |
| 6 | torchhub:NVlabs/RADIO/c-radio_v4-so400m | 256x128    | market1501/official@1 | 0.0631 | 0.1817 | 0.3219 | 0.3893 | 0.0066 |
| 7 | torchhub:NVlabs/RADIO/c-radio_v4-so400m | native     | market1501/official@1 | 0.0472 | 0.1369 | 0.2746 | 0.3453 | 0.0040 |

```mermaid
%%{init: {"themeVariables": {"quadrant1Fill": "transparent", "quadrant2Fill": "transparent", "quadrant3Fill": "transparent", "quadrant4Fill": "transparent", "quadrantExternalBorderStrokeFill": "#999999", "quadrantInternalBorderStrokeFill": "#cccccc", "quadrantPointFill": "#4e79a7"}}}%%
quadrantChart
    title mAP vs mINP (labels are the # column above)
    x-axis "mAP 0.0227" --> "0.0631"
    y-axis "mINP 0.0015" --> "0.0066"
    quadrant-1 " "
    quadrant-2 " "
    quadrant-3 " "
    quadrant-4 " "
    1: [0.0500, 0.0500]
    2: [0.9026, 0.5750]
    3: [0.8634, 0.7164]
    4: [0.5304, 0.5705]
    5: [0.9442, 0.7721]
    6: [0.9500, 0.9500]
    7: [0.5960, 0.4963]
```

```mermaid
%%{init: {"themeVariables": {"xyChart": {"backgroundColor": "transparent", "plotColorPalette": "#4e79a7"}}}}%%
xychart-beta horizontal
    title "mAP by row #"
    x-axis ["1 · 2.27%", "2 · 6.10%", "3 · 5.92%", "4 · 4.43%", "5 · 6.28%", "6 · 6.31%", "7 · 4.72%"]
    y-axis "mAP (%)" 0 --> 6.63
    bar [2.27, 6.10, 5.92, 4.43, 6.28, 6.31, 4.72]
```

## occluded-reid

| # | encoder                                 | resolution | protocol                          | mAP    | R1     | R5     | R10    | mINP   |
|---|-----------------------------------------|------------|-----------------------------------|--------|--------|--------|--------|--------|
| 1 | timm:vit_base_patch16_clip_224.openai   | 224x224    | occluded-reid/occluded-vs-whole@1 | 0.2803 | 0.3540 | 0.5640 | 0.6490 | 0.1264 |
| 2 | torchhub:NVlabs/RADIO/c-radio_v4-h      | 224x224    | occluded-reid/occluded-vs-whole@1 | 0.4560 | 0.5240 | 0.7190 | 0.7940 | 0.2806 |
| 3 | torchhub:NVlabs/RADIO/c-radio_v4-h      | 256x128    | occluded-reid/occluded-vs-whole@1 | 0.4466 | 0.5230 | 0.7160 | 0.7930 | 0.2696 |
| 4 | torchhub:NVlabs/RADIO/c-radio_v4-h      | native     | occluded-reid/occluded-vs-whole@1 | 0.3385 | 0.4170 | 0.6350 | 0.7270 | 0.1786 |
| 5 | torchhub:NVlabs/RADIO/c-radio_v4-so400m | 224x224    | occluded-reid/occluded-vs-whole@1 | 0.4436 | 0.5100 | 0.6990 | 0.7780 | 0.2771 |
| 6 | torchhub:NVlabs/RADIO/c-radio_v4-so400m | 256x128    | occluded-reid/occluded-vs-whole@1 | 0.4401 | 0.5200 | 0.7020 | 0.7720 | 0.2706 |
| 7 | torchhub:NVlabs/RADIO/c-radio_v4-so400m | native     | occluded-reid/occluded-vs-whole@1 | 0.3404 | 0.4140 | 0.6240 | 0.7120 | 0.1850 |

```mermaid
%%{init: {"themeVariables": {"quadrant1Fill": "transparent", "quadrant2Fill": "transparent", "quadrant3Fill": "transparent", "quadrant4Fill": "transparent", "quadrantExternalBorderStrokeFill": "#999999", "quadrantInternalBorderStrokeFill": "#cccccc", "quadrantPointFill": "#4e79a7"}}}%%
quadrantChart
    title mAP vs mINP (labels are the # column above)
    x-axis "mAP 0.2803" --> "0.4560"
    y-axis "mINP 0.1264" --> "0.2806"
    quadrant-1 " "
    quadrant-2 " "
    quadrant-3 " "
    quadrant-4 " "
    1: [0.0500, 0.0500]
    2: [0.9500, 0.9500]
    3: [0.9019, 0.8859]
    4: [0.3482, 0.3547]
    5: [0.8867, 0.9296]
    6: [0.8687, 0.8917]
    7: [0.3578, 0.3920]
```

```mermaid
%%{init: {"themeVariables": {"xyChart": {"backgroundColor": "transparent", "plotColorPalette": "#4e79a7"}}}}%%
xychart-beta horizontal
    title "mAP by row #"
    x-axis ["1 · 28.03%", "2 · 45.60%", "3 · 44.66%", "4 · 33.85%", "5 · 44.36%", "6 · 44.01%", "7 · 34.04%"]
    y-axis "mAP (%)" 0 --> 47.88
    bar [28.03, 45.60, 44.66, 33.85, 44.36, 44.01, 34.04]
```

## vrai

| # | encoder                                 | resolution | protocol                  | mAP    | R1     | R5     | R10    | mINP   |
|---|-----------------------------------------|------------|---------------------------|--------|--------|--------|--------|--------|
| 1 | timm:vit_base_patch16_clip_224.openai   | 224x224    | vrai/train-cross-camera@1 | 0.0251 | 0.0349 | 0.0778 | 0.1043 | 0.0077 |
| 2 | torchhub:NVlabs/RADIO/c-radio_v4-h      | 224x224    | vrai/train-cross-camera@1 | 0.1739 | 0.2152 | 0.3510 | 0.4213 | 0.0805 |
| 3 | torchhub:NVlabs/RADIO/c-radio_v4-h      | 256x128    | vrai/train-cross-camera@1 | 0.1376 | 0.1709 | 0.2850 | 0.3440 | 0.0621 |
| 4 | torchhub:NVlabs/RADIO/c-radio_v4-h      | native     | vrai/train-cross-camera@1 | 0.1936 | 0.2421 | 0.3778 | 0.4434 | 0.0936 |
| 5 | torchhub:NVlabs/RADIO/c-radio_v4-so400m | 224x224    | vrai/train-cross-camera@1 | 0.1489 | 0.1945 | 0.3077 | 0.3712 | 0.0661 |
| 6 | torchhub:NVlabs/RADIO/c-radio_v4-so400m | 256x128    | vrai/train-cross-camera@1 | 0.1268 | 0.1611 | 0.2745 | 0.3364 | 0.0550 |
| 7 | torchhub:NVlabs/RADIO/c-radio_v4-so400m | native     | vrai/train-cross-camera@1 | 0.1603 | 0.2050 | 0.3304 | 0.3937 | 0.0716 |

```mermaid
%%{init: {"themeVariables": {"quadrant1Fill": "transparent", "quadrant2Fill": "transparent", "quadrant3Fill": "transparent", "quadrant4Fill": "transparent", "quadrantExternalBorderStrokeFill": "#999999", "quadrantInternalBorderStrokeFill": "#cccccc", "quadrantPointFill": "#4e79a7"}}}%%
quadrantChart
    title mAP vs mINP (labels are the # column above)
    x-axis "mAP 0.0251" --> "0.1936"
    y-axis "mINP 0.0077" --> "0.0936"
    quadrant-1 " "
    quadrant-2 " "
    quadrant-3 " "
    quadrant-4 " "
    1: [0.0500, 0.0500]
    2: [0.8452, 0.8129]
    3: [0.6511, 0.6197]
    4: [0.9500, 0.9500]
    5: [0.7112, 0.6615]
    6: [0.5935, 0.5450]
    7: [0.7725, 0.7194]
```

```mermaid
%%{init: {"themeVariables": {"xyChart": {"backgroundColor": "transparent", "plotColorPalette": "#4e79a7"}}}}%%
xychart-beta horizontal
    title "mAP by row #"
    x-axis ["1 · 2.51%", "2 · 17.39%", "3 · 13.76%", "4 · 19.36%", "5 · 14.89%", "6 · 12.68%", "7 · 16.03%"]
    y-axis "mAP (%)" 0 --> 20.32
    bar [2.51, 17.39, 13.76, 19.36, 14.89, 12.68, 16.03]
```

# Licenses

## Datasets

| id            | licence                                                  | commercial_ok | gate |
|---------------|----------------------------------------------------------|---------------|------|
| market1501    | research-only                                            | False         | none |
| occluded-reid | academic or educational use only                         | False         | none |
| vrai          | research only — the release prohibits any commercial use | False         | none |

```mermaid
pie showData
    title Commercial use — 3 datasets
    "research / non-commercial only" : 3
```

## Models

| id                                      | licence                   | commercial_ok | gate |
|-----------------------------------------|---------------------------|---------------|------|
| timm:vit_base_patch16_clip_224.openai   | unknown                   | ?             | ?    |
| torchhub:NVlabs/RADIO/c-radio_v4-h      | NVIDIA Open Model License | True          | none |
| torchhub:NVlabs/RADIO/c-radio_v4-so400m | NVIDIA Open Model License | True          | none |

```mermaid
pie showData
    title Commercial use — 3 models
    "commercial use permitted" : 2
    "licence unknown" : 1
```
