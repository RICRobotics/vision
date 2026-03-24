[dataset download](http://jacarini.dinf.usherbrooke.ca/static/dataset/baseline/highway.zip) [datasets from same source](http://jacarini.dinf.usherbrooke.ca/dataset2014)

 - diff.py: in order: translates images to numpy arrays, compares the rgb values, and outputs frames that show when much has changed... run this with: "python3 diff.py input" (input being the same input file from the zip linked above, after moving it to your vision/ directory

 - makevid.py / makevid_win.py - stitches together the image frames from diff.py (or whatever other program you might make)... run this with: "python3 makevid.py output" output being the directory with the frames to stitch together. if you wanted to, you could run "python3 makevid.py input" to stitch together the input. (replace makevid.py with makevid_win.py if you're using windows os.

things you can do:
play around with the threshold value from the default diff.py to see what happens
modify the processing - you can change line 25 of diff.py to manipulate the array however you'd like - just be sure that the output is named "out" so the rest of the script works.
download more datasets from the second link above
