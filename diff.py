# pip install Pillow numpy

from PIL import Image
import numpy as np
import os

INPUT_DIR = "input"
OUTPUT_DIR = "output"
THRESHOLD = 30

images = sorted([f for f in os.listdir(INPUT_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
os.makedirs(OUTPUT_DIR, exist_ok=True)

# for each consecutive set of 2 frames:
for i in range(len(images) - 1):

    # turns the image into an array with dimensions [height x width x 3],
    # height and width being defined by the image size, and 3 for the 3 RGB stream inputs
    img1 = np.array(Image.open(os.path.join(INPUT_DIR, images[i])).convert("RGB"))
    img2 = np.array(Image.open(os.path.join(INPUT_DIR, images[i + 1])).convert("RGB"))


    # compare each RGB value, and sum it up - diff is 2d array [height x width]
    # the maximum value of any element in diff is 765 (255 * 3)
    diff = np.sum(np.abs(img1.astype(int) - img2.astype(int)), axis=2)

    # still a 2d array, same size as diff, but with only 2 possible values (0, 1)
    # compare each value of diff to the THRESHOLD defined above.
    # if less than: 0 (black) else: 1 (white)
    out = np.where(diff >= THRESHOLD, 255, 0).astype(np.uint8)

    # save this new image, as defined by the array out
    out_name = f"dif{i+1:06d}.jpg"
    Image.fromarray(out).save(os.path.join(OUTPUT_DIR, out_name))
    print(f"saved {out_name}")

print("done")
