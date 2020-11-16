#!/bin/sh

ffmpeg -i shh_gradient_50_out_init_zero_ss.mp4 -i shh_gradient_100_out_init_zero_ss.mp4 -i shh_gradient_200_out_init_zero_ss.mp4 -filter_complex hstack=inputs=3 output.mp4
./gifenc.sh output.mp4 ss_init_zero.gif 1500 24
rm -f output.mp4

ffmpeg -i shh_gradient_50_out_ss.mp4 -i shh_gradient_100_out_ss.mp4 -i shh_gradient_200_out_ss.mp4 -filter_complex hstack=inputs=3 output.mp4
./gifenc.sh output.mp4 ss_init_one.gif 1500 24
rm -f output.mp4
