# market1501

| encoder                               | protocol              | mAP    | R1     | R5     | R10    | mINP   |
|---------------------------------------|-----------------------|--------|--------|--------|--------|--------|
| timm:vit_base_patch16_clip_224.openai | market1501/official@1 | 0.0227 | 0.0879 | 0.1829 | 0.2381 | 0.0015 |

# occluded-reid

| encoder                               | protocol                          | mAP    | R1     | R5     | R10    | mINP   |
|---------------------------------------|-----------------------------------|--------|--------|--------|--------|--------|
| timm:vit_base_patch16_clip_224.openai | occluded-reid/occluded-vs-whole@1 | 0.2803 | 0.3540 | 0.5640 | 0.6490 | 0.1264 |

# vrai

| encoder                               | protocol                  | mAP    | R1     | R5     | R10    | mINP   |
|---------------------------------------|---------------------------|--------|--------|--------|--------|--------|
| timm:vit_base_patch16_clip_224.openai | vrai/train-cross-camera@1 | 0.0251 | 0.0349 | 0.0778 | 0.1043 | 0.0077 |

| id                                    | licence                                                  | commercial_ok | gate |
|---------------------------------------|----------------------------------------------------------|---------------|------|
| market1501                            | research-only                                            | False         | none |
| occluded-reid                         | academic or educational use only                         | False         | none |
| timm:vit_base_patch16_clip_224.openai | unknown                                                  | ?             | ?    |
| vrai                                  | research only — the release prohibits any commercial use | False         | none |
