from pathlib import Path
import fabio
import tifffile
import numpy as np
from tqdm import tqdm

RAW_DIR = "raw"
SAVE_DIR = "processed"

raw_files = sorted(list(Path(RAW_DIR).expanduser().glob("*.tif")))
with fabio.open_series(raw_files) as img_series:
    img_0 = img_series.get_frame(0).data
    mask = img_0 >= 0
    img_sum = np.zeros_like(img_0)

    for i in tqdm(range(img_series.nframes)):
        img = img_series.get_frame(i).data
        img = np.clip(img, 0, None)
        img_sum += img
    img_avg = img_sum / img_series.nframes

    Path(SAVE_DIR).mkdir(parents=True, exist_ok=True)
    tifffile.imwrite(Path(SAVE_DIR)/"dark_avg.tif", img_avg)
    tifffile.imwrite(Path(SAVE_DIR)/"mask.tif", np.uint8(mask))