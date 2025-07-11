from pathlib import Path
import fabio
import tifffile
import numpy as np
from scipy.ndimage import maximum_filter

RAW_DIR = "raw"
SAVE_DIR = "processed"

raw_path = Path(RAW_DIR).resolve()
raw_files = sorted(list(raw_path.glob("*.tif")))

with fabio.open_series(raw_files) as img_series:
    img_11 = img_series.get_frame(11).data
    img_11_crop = img_11[540:572, 20:52]

    mask = img_11_crop > 15
    mask_expanded = maximum_filter(mask, size=9)

    Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)
    tifffile.imwrite(Path(SAVE_DIR)/"donut.tif", img_11_crop)
    tifffile.imwrite(Path(SAVE_DIR)/"donut_mask.tif", np.uint8(mask_expanded))

