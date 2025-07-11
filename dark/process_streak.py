from pathlib import Path
import fabio
import numpy as np
import tifffile
from scipy.ndimage import convolve, maximum_filter

RAW_DIR = "raw"
SAVE_DIR = "processed"

raw_path = Path(RAW_DIR).resolve()
raw_files = sorted(list(raw_path.glob("*.tif")))

with fabio.open_series(raw_files) as img_series:
    img_9 = img_series.get_frame(9).data
    img_9_crop = img_9[460:492, 40:72]

    binary = np.uint8(img_9_crop > 0)
    binary_conv = convolve(binary, np.ones((3, 3)), mode='constant', cval=0.0)

    mask = binary_conv >= 3
    mask_expanded = maximum_filter(mask, size=3)

    Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)
    tifffile.imwrite(Path(SAVE_DIR)/"streak.tif", img_9_crop)
    tifffile.imwrite(Path(SAVE_DIR)/"streak_mask.tif", np.uint8(mask_expanded))