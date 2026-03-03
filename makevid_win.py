#!/usr/bin/env python3
"""Make a video from images in a folder (Windows version)."""

# usage: py makevid_win.py <folder>
# requires: ffmpeg in PATH

import subprocess
import sys
import os
import glob

if len(sys.argv) < 2:
    print("usage: py makevid_win.py <folder>")
    sys.exit(1)

folder = sys.argv[1]
foldername = os.path.basename(os.path.normpath(folder))
output = f"{foldername}.mp4"
listfile = os.path.abspath("filelist.txt")

images = sorted(glob.glob(os.path.join(folder, "*.jpg")))
if not images:
    print(f"no jpg files found in {folder}")
    sys.exit(1)

with open(listfile, "w") as f:
    for img in images:
        abspath = os.path.abspath(img).replace("\\", "/")
        f.write(f"file '{abspath}'\n")
        f.write("duration 0.0333\n")

subprocess.run([
    "ffmpeg", "-y",
    "-f", "concat",
    "-safe", "0",
    "-i", listfile,
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    output
], shell=True)

os.remove(listfile)
print(f"saved {output}")
