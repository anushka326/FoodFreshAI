# AgriFreshNET Freshness Dataset Preparation Report

## Overview
- **Total images processed:** 14,160
- **Corrupted/invalid images:** 0
- **Unique physical image stems:** 5,188
- **Random seed:** 42
- **Split strategy:** Grouped stratified split by base image stem and (food, freshness) stratum

## Split Counts
- **Train:** 9,856 images (69.60%)
- **Validation:** 2,131 images (15.05%)
- **Test:** 2,173 images (15.35%)

## Freshness Stage Distribution

| Freshness Stage | Class ID | Train | Validation | Test | Total | Train % | Val % | Test % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fresh** | 0 | 3,296 | 699 | 725 | 4,720 | 69.83% | 14.81% | 15.36% |
| **Semi-Fresh** | 1 | 3,295 | 709 | 716 | 4,720 | 69.81% | 15.02% | 15.17% |
| **Rotten** | 2 | 3,265 | 723 | 732 | 4,720 | 69.17% | 15.32% | 15.51% |

## Food Types Represented (8 varieties)

| Food Type | Fresh (Train/Val/Test) | Semi-Fresh (Train/Val/Test) | Rotten (Train/Val/Test) | Total |
| :--- | :---: | :---: | :---: | :---: |
| **Banana** | 411/90/89 | 413/87/90 | 412/87/91 | 1,770 |
| **Bittermelon** | 412/88/90 | 410/91/89 | 410/90/90 | 1,770 |
| **Cucumber** | 413/88/89 | 413/88/89 | 393/98/99 | 1,770 |
| **Eggplant** | 413/82/95 | 412/91/87 | 407/94/89 | 1,770 |
| **Orange** | 409/90/91 | 415/88/87 | 410/87/93 | 1,770 |
| **Papaya** | 413/84/93 | 408/89/93 | 413/87/90 | 1,770 |
| **Pineapple** | 412/89/89 | 411/87/92 | 408/92/90 | 1,770 |
| **Tomato** | 413/88/89 | 413/88/89 | 412/88/90 | 1,770 |

## Leak-Free Guarantee
- All augmented variations derived from the same base photograph (`base_stem`) reside in the exact same split.
- Base stem intersection between splits is strictly **0**.
