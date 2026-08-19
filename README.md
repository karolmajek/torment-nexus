# torment-nexus - ReID framework
what a time to be alive



# Datasets
## VeRi-776 datasets/VeRi [liu2017provid]
- 50,000 images of 776 vehicles
- where 37,781 images of 576 vehicles are employed as training set,
- while 11,579 images of 200 vehicles are employed as a test set.
- A subset of 1,678 images in the test set generates the query set

## VehicleID [liu2016deep]
- real-world scenario,
- contains 221,763 images corresponding to 26,267 vehicles in total.

## DukeMTMC / ANY Duke-derived WILL NOT BE USED

# Evaluation metrics

## VehicleID

From the original testing data, four subsets, which contain 800, 1,600, 2,400 and 3,200 vehicles, are extracted for vehicle search for multi-scales.
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
@inproceedings{liu2016deep,
  title={Deep relative distance learning: Tell the difference between similar vehicles},
  author={Liu, Hongye and Tian, Yonghong and Yang, Yaowei and Pang, Lu and Huang, Tiejun},
  booktitle={Proceedings of the IEEE conference on computer vision and pattern recognition},
  pages={2167--2175},
  year={2016}
}
```