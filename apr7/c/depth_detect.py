import cv2
import numpy as np
from transformers import pipeline
from PIL import Image
from pathlib import Path

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

depth_estimator = pipeline("depth-estimation", model="LiheYoung/depth-anything-small-hf")


def estimate_depth(input_path, output_path):

    img = cv2.imread(str(input_path))
    # resize to smaller image for faster processing
    small = cv2.resize(img, (320, int(320 * img.shape[0] / img.shape[1])))

    # convert to PIL format which is needed for the model
    pil_image = Image.fromarray(cv2.cvtColor(small, cv2.COLOR_BGR2RGB))

    depth = np.array(depth_estimator(pil_image)["depth"])
    depth = cv2.resize(depth, (img.shape[1], img.shape[0]))


    # normalize to 0-255 range
    depth = cv2.normalize(depth, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # changes grayscaled to color mapping for more interesting viewing
    depth = cv2.applyColorMap(depth, cv2.COLORMAP_INFERNO)

    cv2.imwrite(str(output_path), depth)


for image_path in INPUT_DIR.glob("*.jpg"):
    output = OUTPUT_DIR / f"{image_path.stem}_depth.jpg"
    estimate_depth(image_path, output)
    print(f"Processed: {image_path.name}")
