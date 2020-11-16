import os
import sys
import argparse
from matplotlib import cm, ticker
import matplotlib.pyplot as plt
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
import numpy as np
from glob import glob
import shutil
import traceback
import warnings

plt.switch_backend("agg")

SHIFT = 1e-10
SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
GIFENC_PATH = os.path.join(SCRIPT_PATH, "gifenc.sh")


def plot_solver_matrix(solver, vmin=None, vmax=None, figname=None):
    # TODO: fix LogNorm issue: now shifting by SHIFT to avoid issue with 0.0
    # TODO: ticks and label formatting for colobar
    # https://stackoverflow.com/questions/35728665/matplotlib-colorbar-tick-label-formatting
    try:
        mat = np.load(solver)
    except IOError:
        print("IOError: {0}".format(IOError))
        raise IOError("Solver output: {:s} cannot be opened".format(solver))

    aspect = 20
    pad_fraction = 0.5
    width_to_height = mat.shape[0] / mat.shape[1]

    mat += SHIFT
    if not vmin and not vmax:
        vmin = np.min(mat)
        vmax = np.max(mat)
    norm = mpl.colors.LogNorm(vmin=vmin, vmax=vmax)
    cmap = "coolwarm"
    mappable = cm.ScalarMappable(norm=norm, cmap="coolwarm")

    height = 5
    width = height * width_to_height + 2

    fig = plt.figure(figsize=(width, height))
    ax = plt.gca()
    # img = ax.pcolor(X, Y, mat.T, norm=norm, cmap=cmap)
    img = ax.imshow(
        mat.T,
        norm=norm,
        cmap=cmap,
    )
    ax.set_xlabel("X (LBM unit)")
    ax.set_ylabel("Y (LBM unit)")
    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    divider = make_axes_locatable(ax)
    width = axes_size.AxesY(ax, aspect=1.0 / aspect)
    pad = axes_size.Fraction(pad_fraction, width)
    cax = divider.append_axes("right", size=width, pad=pad)
    cbar = plt.colorbar(mappable, cax=cax)
    cbar.set_label("Shh gradient (log)")
    plt.tight_layout()
    if figname:
        plt.savefig(figname, dpi=300, transparent=False)
        plt.close(fig)


# https://stackoverflow.com/questions/16915966/using-matplotlib-animate-to-animate-a-contour-plot-in-python
# https://stackoverflow.com/questions/32455162/how-to-plot-contourf-colorbar-in-different-subplot-matplotlib
# Generate grid for plotting
def plot_solver_matrix_dir(dir, steps=10):
    # consistent vmax vmin for colorbar
    vmin, vmax = 1e-7, 1e-7
    count = 0

    # set the min and max to be the same scale for one batch
    for i, solver_npy in enumerate(glob("{:s}/Cells_*.npy".format(dir))):
        mat = np.load(solver_npy)
        mat_min = np.min(mat)
        mat_max = np.max(mat)
        if vmin > mat_min:
            vmin = mat_min
        if vmax <= mat_max:
            vmax = mat_max

        count += 1

    # create dir for fig
    fig_dir = os.path.join(dir, "fig")
    if not os.path.exists(fig_dir):
        try:
            os.mkdir(fig_dir)
            print("Creating {:s}...".format(fig_dir))
        except OSError:
            print("Creating {:s} failed!".format(fig_dir))
            sys.exit(1)
    else:
        print("{:s} exist...".format(fig_dir))

    for i in range(0, count):
        solver = os.path.join(dir, "Cells_{:d}.npy".format(steps * i))
        plot_solver_matrix(
            solver=solver,
            vmin=vmin + SHIFT,
            vmax=vmax + SHIFT,
            figname="{:s}/solver_{:d}.png".format(fig_dir, i),
        )


def convert_mp4_gif(dir):
    warnings.warn(
        "Now this has only been tested on ffmpeg version 4.3.1 Copyright (c) 2000-2020 the FFmpeg developers"
    )

    fig_dir = "{:s}/fig".format(dir)

    convert_vid = "ffmpeg -loglevel panic -y -f image2 -framerate 10 -i {}/solver_%d.png {}/solver.mp4".format(
        fig_dir, fig_dir
    )
    convert_gif = "{} {}/solver.mp4 {}/solver.gif".format(GIFENC_PATH, fig_dir, fig_dir)

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
    parser.add_argument(
        "--vid",
        action="store_true",
        help="Whether or not convert pics into mp4 and gif",
    )
    parser.add_argument("--name", type=str, help="Name for mp4 gif")
    args = parser.parse_args()

    name = args.name
    if not name:
        name = os.path.basename(os.path.normpath(args.input_dir))

    try:
        plot_solver_matrix_dir(args.input_dir, args.step)
    except:
        print("Drawing error")
        traceback.print_exc()
        sys.exit(1)

    if args.vid:
        try:
            convert_mp4_gif(args.input_dir)
        except:
            print("Conversion error")
            traceback.print_exc()
            sys.exit(1)

        try:
            shutil.copy(
                "{}/fig/solver.mp4".format(args.input_dir),
                "./{:s}_solver.mp4".format(name),
            )
            shutil.copy(
                "{}/fig/solver.gif".format(args.input_dir),
                "./{:s}_solver.gif".format(name),
            )
            print("Copied to ./{:s}_solver.mp4".format(name))
            print("Copied to ./{:s}_solver.mp4".format(name))
        except:
            print("Copying error")
