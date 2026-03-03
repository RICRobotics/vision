#!/usr/bin/env python3
"""Make a video from images in a folder."""

import subprocess
import sys
import os

if len(sys.argv) < 2:
    print("usage: python makevid.py <folder>")
    sys.exit(1)

folder = sys.argv[1]
output = f"{folder}.mp4"

subprocess.run([
    "ffmpeg", "-y",
    "-framerate", "30",
    "-pattern_type", "glob",
    "-i", f"{folder}/*.jpg",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    output
])

print(f"saved {output}")
