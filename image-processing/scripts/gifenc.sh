#!/bin/sh
# based on https://github.com/thevangelist/FFMPEG-gif-script-for-bash

INPUT=${1:-input.mp4}
OUTPUT=${2:-output.gif}
X_RES=${3:-500}
FPS=${4:-24}

if test $# -lt 2; then
	cat <<-EOH
		$0: Script to generate animated gifs easily from command line.

		Usage:

		$0 input.(mp4|avi|webm|flv|...) output.gif horizontal_resolution=500 fps=24
	EOH
	exit 1
fi

PALETTE="/tmp/ffmpeg2gifXXXXXX.png"

FILTERS="fps=$FPS,scale=$X_RES:-1:flags=lanczos"

ffmpeg -loglevel panic -i "$INPUT" -vf "$FILTERS,palettegen" -y "$PALETTE"
ffmpeg -loglevel panic -i "$INPUT" -i $PALETTE -lavfi "$FILTERS [x]; [x][1:v] paletteuse" "$OUTPUT"

rm -f "$PALETTE"
