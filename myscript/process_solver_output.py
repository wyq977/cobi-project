import os
import sys
import argparse
import numpy as np
from glob import glob


def save_solver_as_mat(filename, size_x, size_y):
    # transform solver output for numpy

    try:
        f_out = open(filename, "r")
    except IOError:
        print("Solver output {} cannot be opened".format(filename))
        sys.exit(1)

    arr = np.ndarray((size_x, size_y), dtype=float)

    for line in f_out.readlines():
        line_list = line.rstrip("\n").split("\t")
        x = int(line_list[0])
        y = int(line_list[1])
        c = line_list[5]
        arr[x, y] = c

    f_out.close()

    filename_no_ext, _ = os.path.splitext(filename)
    np.save("{}.npy".format(filename_no_ext), arr)  # save binary file for future


if __name__ == "__main__":

    # Set up the parsing of command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input_dir", type=str, required=True, help="LBIBCell reporter output dir"
    )
    parser.add_argument(
        "--size_x", type=int, required=True, default=300, help="SizeX in LBIBCell"
    )
    parser.add_argument(
        "--size_y", type=int, required=True, default=1000, help="SizeY in LBIBCell"
    )
    args = parser.parse_args()

    for solver_output in glob("{:s}/Cells_*.txt".format(args.input_dir)):
        # cells_idx, _ = os.path.splitext(os.path.basename(solver_output))
        # cells_idx, _ = os.path.splitext(solver_output)
        save_solver_as_mat(solver_output, args.size_x, args.size_y)
