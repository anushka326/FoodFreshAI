# AgriFreshNET Quality & Domain Suitability Audit (V3)

- **Total Dataset Images:** 14,160 images across 24 folders
- **Sample Audited for Verification:** 2400 images (100 images per folder)
- **Corrupt / Unreadable Files:** 0
- **Uniform Native Resolution:** 512 $	imes$ 512 pixels (Aspect ratio: 1:1)
- **Color Space Mode:** RGB (24-bit TrueColor, 0 grayscale, 0 alpha channels)
- **Extreme / Non-Standard Resolutions:** 0
- **Exact Hash Duplicates:** 36 duplicate hash clusters (40 redundant files across 14,120 unique image hashes)
- **Inter-Stage Day-9 Duplicates:** 17 images shared between `Fresh Orange(1-9)` and `Semi fresh Orange(9-20)`

## Real-World Characteristics Analysis
1. **Background Variation:**
   Unlike Fruits-360 which strictly features synthetic, pure-white `#FFFFFF` rotary discs, AgriFreshNET exhibits natural domestic backgrounds:
   - Kitchen countertops and wooden tables (mean corner RGB ranging from [91, 90, 87] to [220, 220, 223]).
   - Household tablecloths and textured paper backdrops.
2. **Illumination & Camera Conditions:**
   - Filenames preserve smartphone camera EXIF cues: `HDR_AE`, `WA0015` (WhatsApp mobile photo transfer), and Android timestamps (`IMG_2025...`).
   - Natural ambient lighting variations with directional shadows and varying exposure levels.
3. **Object Scale & Pose:**
   - Realistic produce scale occupying 40%–85% of frame area.
   - Multiple angles: top-down, tilted perspective, lateral views.
4. **Food Presentation:**
   - Whole uncut produce as well as produce in realistic deterioration states (bruising, fungal spots, moisture loss).
   - Crucial for food classification robustness: prevents models from assuming food is only identifiable when pristine.

## Domain Gap & Limitations for V3
1. **Vocabulary Coverage:** AgriFreshNET covers only **7 of the 24** Food Recognition V2 categories (29.2% of target classes). The remaining 17 categories (e.g. Apple, Pomegranate, Onion, Mango) have zero AgriFreshNET coverage.
2. **Augmentation Burst Frames:** High proportion of consecutive frames generated from physical base photos. Group-based splitting by base stem is mandatory to avoid train/val/test leakage.
3. **Unmatched Class:** Contains `Bittermelon` (1,770 images), which is not part of the 24 V2 food classes.
