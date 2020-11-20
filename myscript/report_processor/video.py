from .settings import warning

# from myproject.models import some_model
import os

# taken from https://github.com/taichi-dev/taichi/blob/master/python/taichi/tools/video.py
# Write the frames to the disk and then make videos (mp4 or gif) if necessary


def get_convert_path():
    return "convert"


def png_to_gif(input_files, frame_rate=24, output_path="output.gif"):
    # TODO: add more robust way to handle png
    if isinstance(input_files, str):
        warning(
            "Using wildcard and sort like "
            ' "convert -delay 10 -loop 0 *png ~/Desktop/Test_convert_wildcard.gif" \n'
            "Please change it in the future ",
            UserWarning,
            1,
        )

        delay = 100 / frame_rate
        command = (
            (get_convert_path() + " -delay {:.2f} ".format(delay))
            + "-loop 0 "
            + "$(ls -1 {:s} | sort -V) ".format(input_files)
            + output_path
        )
        print(command)
    else:
        assert (
            'input_files should be list (of files) or str (of file template, like "%04d.png") instead of '
            + str(type(input_files))
        )
    pass


__all__ = [
    "png_to_gif",
    "get_convert_path",
]