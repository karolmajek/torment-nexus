# Datasets

## market1501

| encoder                                 | resolution | protocol              | mAP    | R1     | R5     | R10    | mINP   |
|-----------------------------------------|------------|-----------------------|--------|--------|--------|--------|--------|
| timm:vit_base_patch16_clip_224.openai   | 224x224    | market1501/official@1 | 0.0227 | 0.0879 | 0.1829 | 0.2381 | 0.0015 |
| torchhub:NVlabs/RADIO/c-radio_v4-h      | 224x224    | market1501/official@1 | 0.0610 | 0.1838 | 0.3207 | 0.3955 | 0.0044 |
| torchhub:NVlabs/RADIO/c-radio_v4-h      | 256x128    | market1501/official@1 | 0.0592 | 0.1799 | 0.3224 | 0.3955 | 0.0052 |
| torchhub:NVlabs/RADIO/c-radio_v4-so400m | 224x224    | market1501/official@1 | 0.0628 | 0.1832 | 0.3180 | 0.3869 | 0.0055 |
| torchhub:NVlabs/RADIO/c-radio_v4-so400m | 256x128    | market1501/official@1 | 0.0631 | 0.1817 | 0.3219 | 0.3893 | 0.0066 |

## occluded-reid

| encoder                                 | resolution | protocol                          | mAP    | R1     | R5     | R10    | mINP   |
|-----------------------------------------|------------|-----------------------------------|--------|--------|--------|--------|--------|
| timm:vit_base_patch16_clip_224.openai   | 224x224    | occluded-reid/occluded-vs-whole@1 | 0.2803 | 0.3540 | 0.5640 | 0.6490 | 0.1264 |
| torchhub:NVlabs/RADIO/c-radio_v4-h      | 224x224    | occluded-reid/occluded-vs-whole@1 | 0.4560 | 0.5240 | 0.7190 | 0.7940 | 0.2806 |
| torchhub:NVlabs/RADIO/c-radio_v4-h      | 256x128    | occluded-reid/occluded-vs-whole@1 | 0.4466 | 0.5230 | 0.7160 | 0.7930 | 0.2696 |
| torchhub:NVlabs/RADIO/c-radio_v4-so400m | 224x224    | occluded-reid/occluded-vs-whole@1 | 0.4436 | 0.5100 | 0.6990 | 0.7780 | 0.2771 |
| torchhub:NVlabs/RADIO/c-radio_v4-so400m | 256x128    | occluded-reid/occluded-vs-whole@1 | 0.4401 | 0.5200 | 0.7020 | 0.7720 | 0.2706 |

## vrai

| encoder                                 | resolution | protocol                  | mAP    | R1     | R5     | R10    | mINP   |
|-----------------------------------------|------------|---------------------------|--------|--------|--------|--------|--------|
| timm:vit_base_patch16_clip_224.openai   | 224x224    | vrai/train-cross-camera@1 | 0.0251 | 0.0349 | 0.0778 | 0.1043 | 0.0077 |
| torchhub:NVlabs/RADIO/c-radio_v4-h      | 224x224    | vrai/train-cross-camera@1 | 0.1739 | 0.2152 | 0.3510 | 0.4213 | 0.0805 |
| torchhub:NVlabs/RADIO/c-radio_v4-h      | 256x128    | vrai/train-cross-camera@1 | 0.1376 | 0.1709 | 0.2850 | 0.3440 | 0.0621 |
| torchhub:NVlabs/RADIO/c-radio_v4-so400m | 224x224    | vrai/train-cross-camera@1 | 0.1489 | 0.1945 | 0.3077 | 0.3712 | 0.0661 |
| torchhub:NVlabs/RADIO/c-radio_v4-so400m | 256x128    | vrai/train-cross-camera@1 | 0.1268 | 0.1611 | 0.2745 | 0.3364 | 0.0550 |

# Licenses

| id                                      | licence                                                  | commercial_ok | gate |
|-----------------------------------------|----------------------------------------------------------|---------------|------|
| market1501                              | research-only                                            | False         | none |
| occluded-reid                           | academic or educational use only                         | False         | none |
| timm:vit_base_patch16_clip_224.openai   | unknown                                                  | ?             | ?    |
| torchhub:NVlabs/RADIO/c-radio_v4-h      | NVIDIA Open Model License                                | True          | none |
| torchhub:NVlabs/RADIO/c-radio_v4-so400m | NVIDIA Open Model License                                | True          | none |
| vrai                                    | research only — the release prohibits any commercial use | False         | none |
