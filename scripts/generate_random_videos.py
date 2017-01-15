#!/usr/bin/python

# This script generates random video files of 1s length with the sha1 checksum a number as the filename, and burned into the video

import os
import hashlib
import sys
import subprocess

if len(sys.argv) != 2:
    print "usage: %s <number>" % sys.argv[0]
    exit(1)

num = int(sys.argv[1])

print num


for i in range(1, num):
    checksum = hashlib.sha1()
    checksum.update("%d" % i)
    txt = checksum.hexdigest()
    dir = "%s/%s" % (txt[0:3], txt[3:6])
    path = "%s/%s.mov" % (dir, txt)
    try:
        os.makedirs(dir)
    except:
        pass

    if not os.path.exists(path):
        cmd = "ffmpeg -y -f lavfi -i color=c=black:s=640x480 -vf 'drawtext=text=%s:fontcolor=white:fontsize=32:x=(w-tw)/2:y=h/2' -t 1 -c:v libx264 -pix_fmt yuv420p -r 25  %s" % (txt, path)
        subprocess.call(cmd, shell=True)
