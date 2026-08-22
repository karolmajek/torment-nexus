# torment-nexus - ReID framework
what a time to be alive



# Datasets

**[datasets/](datasets/) is the single source of truth.** One page per dataset — contents, splits,
counts, licence, and how to obtain it — plus `get.py` (`ls · show · fetch · verify`), which reads
those same pages. Counts are not repeated anywhere else in this repository, including here: the
copy that used to live in this file disagreed with the release about VeRi's training set size.

```bash
python datasets/get.py ls
python datasets/get.py counts veri776
```

- [VeRi-776](datasets/veri776.md) — vehicles; also this project's evaluator oracle [liu2017provid]
- [VehicleID](datasets/vehicleid.md) — vehicles, front/rear only [liu2016deep]
- [VRAI](datasets/vrai.md) — vehicles from a drone; the test identities are not in the
  release, so the only protocol that scores offline is over its training split [Wang2019vehicle]
- [MSMT17](datasets/msmt17.md), [Market-1501](datasets/market1501.md),
  [CUHK03-NP](datasets/cuhk03-np.md), [Occluded-REID](datasets/occluded-reid.md),
  [CCVID](datasets/ccvid.md), [MARS](datasets/mars.md) — people
- [Market-1501 +500k](datasets/market1501-500k.md) — the same 3,368 queries against a gallery
  27x larger. It measures how fast a score decays with gallery size, which is the axis every
  other benchmark holds fixed and never reports [zheng2015scalable]
- [VERI-Wild](datasets/veri-wild.md), [SOMA](datasets/soma.md),
  [Market-1501 Attribute](datasets/market1501-attribute.md)

## DukeMTMC / ANY Duke-derived WILL NOT BE USED

Denied in code, with no override flag, in both `datasets/get.py` and `reidbench.provenance`.
Reasoning and substitutes: [datasets/dukemtmc-denied.md](datasets/dukemtmc-denied.md).

# Evaluation metrics

## VehicleID

Four test subsets by identity count, each drawn repeatedly and averaged — sizes and draw count on
[its page](datasets/vehicleid.md); the subset size belongs in the protocol name.
- CMC curve and
- mAP are employed to evaluate the overall performance for all test images.
- For each query, its average precision (AP) is computed from the precision-recall curve.






# Bib

```
@article{liu2017provid,
  title={Provid: Progressive and multimodal vehicle reidentification for large-scale urban surveillance},
  author={Liu, Xinchen and Liu, Wu and Mei, Tao and Ma, Huadong},
  journal={IEEE Transactions on Multimedia},
  volume={20},
  number={3},
  pages={645--658},
  year={2017},
  publisher={IEEE}
}
@inproceedings{zheng2015scalable,
  title={Scalable Person Re-identification: A Benchmark},
  author={Zheng, Liang and Shen, Liyue and Tian, Lu and Wang, Shengjin and Wang, Jingdong and Tian, Qi},
  booktitle={Proceedings of the IEEE International Conference on Computer Vision},
  pages={1116--1124},
  year={2015}
}
@inproceedings{liu2016deep,
  title={Deep relative distance learning: Tell the difference between similar vehicles},
  author={Liu, Hongye and Tian, Yonghong and Yang, Yaowei and Pang, Lu and Huang, Tiejun},
  booktitle={Proceedings of the IEEE conference on computer vision and pattern recognition},
  pages={2167--2175},
  year={2016}
}
```