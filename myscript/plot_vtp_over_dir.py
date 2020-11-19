import os
import sys
import argparse
import pyvista as pv
from pyvista import examples
import numpy as np
from glob import glob
import traceback

CAMERA_POS = [(125, 505, 2200), (125, 505, 0), (0, 1, 0)]  # only for 300 x 1000 box


def plot_mesh_with_cell_type(filename, figname):

    mesh = pv.read(filename)
    # TODO: Fix colorbar location and camera location
    # TODO: change canvas resolution
    # cell_type = mesh["cell_type"]
    # blue = np.array([12 / 256, 238 / 256, 246 / 256, 1])
    # red = np.array([1, 0, 0, 1])
    # mapping = np.array([0.0, 1.0])
    # my_colormap = ListedColormap(newcolors)
    mesh.plot(
        cpos=CAMERA_POS,
        scalars="cell_type",
        show_edges=True,
        color=True,
        off_screen=True,
        screenshot=figname,
    )


def plot_mesh_dir(dir, steps=10):
    # assume
    count = len(glob("{:s}/Cells_*.vtm".format(dir)))
    if count == 0:
        print("No cell reporter files saved, exiting...")
        sys.exit(1)

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
        filename = os.path.join(
            dir, "Cells_{:d}/".format(steps * i), "Cells_{:d}_0.vtp".format(steps * i)
        )
        figname = os.path.join(fig_dir, "Cells_{:d}_cell_type.png".format(i))
        print("Ploting mesh {:s}".format(figname))
        print("Saving plot to {:s}".format(figname))
        plot_mesh_with_cell_type(
            filename=filename,
            figname=figname,
        )


if __name__ == "__main__":

    # Set up the parsing of command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir", type=str, required=True, help="LBIBCell reporter output dir"
    )
    parser.add_argument(
        "--step", type=int, required=True, default=10, help="Steps in LBIBCell"
    )
    args = parser.parse_args()

    try:
        plot_mesh_dir(args.input_dir, args.step)
    except:
        print("Drawing error")
        traceback.print_exc()
        sys.exit(1)

