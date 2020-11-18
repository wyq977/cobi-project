#!/bin/sh
# TODO: add wildcard support from argument
# https://stackoverflow.com/questions/34521320/using-a-glob-expression-passed-as-a-bash-script-argument
# https://stackoverflow.com/questions/20368577/bash-wildcard-n-digits
dir=${1}
gif=${2}
wildcard=${3}
FILES=("${dir}/${wildcard}"*.png)

if test $# -lt 3; then
	cat <<-EOH
	$0: Script to generate animated gifs easily from command line by convert by Imagemagick

	Usage:

	$0 input_dir output.gif wildcard_for_png(i.e. solver_%d)
	EOH
    exit 1
fi


NB_OF_PNG=$(ls -1 "${FILES[@]}" | wc -l)
if test $NB_OF_PNG -eq 3; then
	printf "\nNo png found using wildcard: ${FILES}\n\n"
    exit 1
else
	printf "\n${NB_OF_PNG} png found, converting to ${gif}...\n\n"
fi


convert -delay 10 -loop 0 $(ls -1 "${FILES[@]}" | sort -V) "${gif}"


