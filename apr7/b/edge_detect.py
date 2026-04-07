import cv2
import numpy as np
from pathlib import Path

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

SOBEL_X = np.array([
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]
], dtype=np.float64)

SOBEL_Y = np.array([
    [-1, -2, -1],
    [ 0,  0,  0],
    [ 1,  2,  1]
], dtype=np.float64)


def normalize_to_image(array):
    return cv2.normalize(array, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


# does everything with cv2 functions, so harder to understand w/o reading documentation, 
# but _much_ faster, because the backend is C rather than python.
def detect_edges(input_path, output_x, output_y, output_combined):
    grayscale = cv2.imread(str(input_path), cv2.IMREAD_GRAYSCALE)

    edges_x = cv2.filter2D(grayscale, cv2.CV_64F, SOBEL_X)
    edges_y = cv2.filter2D(grayscale, cv2.CV_64F, SOBEL_Y)
    magnitude = np.sqrt(edges_x ** 2 + edges_y ** 2)

    cv2.imwrite(str(output_x), normalize_to_image(edges_x))
    cv2.imwrite(str(output_y), normalize_to_image(edges_y))
    cv2.imwrite(str(output_combined), normalize_to_image(magnitude))


for image_path in INPUT_DIR.glob("*.jpg"):
    stem = image_path.stem
    detect_edges(
        image_path,
        OUTPUT_DIR / f"{stem}_x.jpg",
        OUTPUT_DIR / f"{stem}_y.jpg",
        OUTPUT_DIR / f"{stem}_edges.jpg"
    )
    print(f"Processed: {image_path.name}")
