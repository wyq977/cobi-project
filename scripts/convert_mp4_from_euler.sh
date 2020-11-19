#!/bin/sh

input=$1
output=$2

tmpdir="./tmp23213"

scp -q -r wangyong@euler.ethz.ch:$input/fig $tmpdir

ffmpeg -loglevel panic -y -f image2 -framerate 10 -i $tmpdir/contourf_%d.png $output.mp4
./gifenc.sh $output.mp4 $output.gif

rm -rf $tmpdir
