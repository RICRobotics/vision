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
])

SOBEL_Y = np.array([
    [-1, -2, -1],
    [ 0,  0,  0],
    [ 1,  2,  1]
])


def convolve(image, kernel):
    height, width = image.shape
    kernel_height, kernel_width = kernel.shape
    pad_height = kernel_height // 2
    pad_width = kernel_width // 2

    # "frame" the actual information of the image in 0s
    padded = np.zeros((height + 2 * pad_height, width + 2 * pad_width))
    padded[pad_height : pad_height + height, pad_width : pad_width + width] = image

    # make an empty array which will be the output
    output = np.zeros((height, width))

    for y in range(height):
        for x in range(width):
            # region is the part of the actual image with the same dimensions as the kernel
            region = padded[y : y + kernel_height, x : x + kernel_width]

            # this does element wise multiplication, then adds them up.
            output[y, x] = np.sum(region * kernel)

    return output


def normalize_to_image(array):
    return cv2.normalize(array, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


def detect_edges(input_path, output_path_x, output_path_y):
    # make grayscale image - this does not consider color.
    grayscale = cv2.imread(str(input_path), cv2.IMREAD_GRAYSCALE).astype(np.float64)

    # use the function as defined above to make the two arrays
    edges_x = convolve(grayscale, SOBEL_X)
    edges_y = convolve(grayscale, SOBEL_Y)

    # actually makes the images in the dir - important: normalize_to_image is a cv2 function which:
    # takes all the inputs of the array, makes the smallest map to 0, the largest map to 255, and the rest are fit linearly.
    cv2.imwrite(str(output_path_x), normalize_to_image(edges_x))
    cv2.imwrite(str(output_path_y), normalize_to_image(edges_y))


for image_path in INPUT_DIR.glob("*.jpg"):
    stem = image_path.stem
    output_x = OUTPUT_DIR / f"{stem}_x.jpg"
    output_y = OUTPUT_DIR / f"{stem}_y.jpg"

    detect_edges(image_path, output_x, output_y)
    print(f"Processed: {image_path.name}")
