import os
import sys
import argparse
from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.animation as animation
import numpy as np
from glob import glob
import shutil

# https://stackoverflow.com/questions/16915966/using-matplotlib-animate-to-animate-a-contour-plot-in-python
# https://stackoverflow.com/questions/32455162/how-to-plot-contourf-colorbar-in-different-subplot-matplotlib
# Generate grid for plotting
def draw_contourf(dir, steps=10):
    # consistent max for colorbar
    vmin, vmax = 0.0, 0.0
    size_x, size_y = 0, 0
    count = 0

    for i, solver_npy in enumerate(glob("{:s}/Cells_*.npy".format(dir))):
        mat = np.load(solver_npy)
        mat_min = np.min(mat)
        mat_max = np.max(mat)
        if vmin > mat_min:
            vmin = mat_min
        if vmax <= mat_max:
            vmax = mat_max
        if i == 0:
            size_x, size_y = mat.shape

        count += 1

    x = np.linspace(0, size_x - 1, size_x, dtype=int)
    y = np.linspace(0, size_y - 1, size_y, dtype=int)
    X, Y = np.meshgrid(x, y)

    fig = plt.figure(figsize=(5, 10))
    gs = mpl.gridspec.GridSpec(
        nrows=1, ncols=2, height_ratios=[1], width_ratios=[19, 1]
    )
    ax1 = fig.add_subplot(gs[0, 0])  # contourf
    ax2 = fig.add_subplot(gs[0, 1])  # colorbar
    cmap = plt.cm.plasma
    norm = mpl.colors.Normalize(vmin, vmax)
    cbar = mpl.colorbar.ColorbarBase(ax2, cmap=cmap, norm=norm)

    # create dir for fig
    fig_dir = "{:s}/fig".format(dir)
    if not os.path.exists(fig_dir):
        try:
            os.mkdir(fig_dir)
        except OSError:
            print("Creation of the directory {:s} failed".format(fig_dir))
            sys.exit(1)
    # else:
    #     for f in os.listdir(fig_dir):
    #         os.remove(os.path.join(fig_dir, f))

    for i in range(0, count):
        solver_npy = "{:s}/Cells_{:d}.npy".format(dir, steps * i)
        mat = np.load(solver_npy)
        ax1.contourf(X.T, Y.T, mat, cmap=cmap, vmin=vmin, vmax=vmax)
        fig.savefig("{:s}/contourf_{:d}.png".format(fig_dir, i), dpi=300)
        ax1.cla()
        # ax2.cla() # dont clear colorbar


def convert_mp4_gif(dir):
    fig_dir = "{:s}/fig".format(dir)

    print("Converting contourf into vid and gif")

    convert_vid = "ffmpeg -loglevel panic -y -f image2 -framerate 10 -i {}/contourf_%d.png {}/contourf.mp4".format(
        fig_dir, fig_dir
    )
    convert_gif = "./gifenc.sh {}/contourf.mp4 {}/contourf.gif".format(fig_dir, fig_dir)

    try:
        if os.system(convert_vid) != 0:
            print("mp4 are not converted")
        if os.system(convert_gif) != 0:
            print("mp4 are not converted")
    except:
        print("ffmpeg convert does not work")


if __name__ == "__main__":

    # Set up the parsing of command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir", type=str, required=True, help="LBIBCell reporter output dir"
    )
    parser.add_argument(
        "--step", type=int, required=True, default=10, help="Steps in LBIBCell"
    )
    parser.add_argument("--name", type=str, help="Name for mp4 gif")
    args = parser.parse_args()

    name = args.name
    if not name:
        name = os.path.basename(os.path.normpath(args.input_dir))

    try:
        draw_contourf(args.input_dir, args.step)
    except:
        print("Drawing error")

    try:
        convert_mp4_gif(args.input_dir)
    except:
        print("Conversion error")

    try:
        shutil.copy(
            "{}/fig/contourf.mp4".format(args.input_dir),
            "./{:s}_contourf.mp4".format(name),
        )
        shutil.copy(
            "{}/fig/contourf.gif".format(args.input_dir),
            "./{:s}_contourf.gif".format(name),
        )
        print("Copied to ./{:s}_contourf.mp4".format(name))
        print("Copied to ./{:s}_contourf.mp4".format(name))
    except:
        print("Copying error")
