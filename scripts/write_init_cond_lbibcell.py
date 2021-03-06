"""
write_init_cond_lbibcell

Write a initial round cell for LBIBCell simulation as well as the parameters

Author: Yongqi Wang <wangyong@student.ethz.ch>
"""
import os
import sys
import argparse
from math import cos, sin, pi

from numpy.core.defchararray import center


def create_points_on_cell(radius, center, res):
    """Create points on circle with set angle resolution

    Parameters
    ----------
    radius : float
        the radius of cell
    center : tuple of float
        Coordinate center of circle
    res : int
        Coordinate center of circle, by default 360

    Returns
    -------
    x_pos : list of float
        A list of all the X coordinates
    y_pos : list of float
        A list of all the Y coordinates
    """
    x_pos, y_pos = [], []
    center_x, center_y = center

    for i in range(res):
        angle = (2 * pi) * (i / res)
        x = center_x + (radius * cos(angle))
        y = center_y + (radius * sin(angle))
        x_pos.append(x)
        y_pos.append(y)

    return x_pos, y_pos


def write_circle_points_lbibcell(
    center,
    radius,
    res=360,
    filename="parameters.txt",
):
    """Write the points in plain text per LBIBCell standard


    Parameters
    ----------
    radius : float
        the radius of cell
    center : tuple of float
        Coordinate center of circle
    res : int
        Coordinate center of circle, by default 360
    filename : str, optional
        Path to the parameter file, by default "parameters.txt"

    .. _See LBIBCell Doc on format: https://tanakas.bitbucket.io/lbibcell/tutorial_01.html#textinput

    """
    x_pos, y_pos = create_points_on_cell(radius, center, res)

    try:
        f_out = open(filename, "w")
    except IOError:
        print("Output file {} cannot be created".format(filename))
        sys.exit(1)

    # Write header for position and position data
    f_out.write("{}\t{}\t{}\n".format("#Nodes (id", "xPos", "yPos)"))

    for i in range(res):
        f_out.write("{}\t{}\t{}\n".format(i + 1, x_pos[i], y_pos[i]))

    # Write header for position again for format reason
    f_out.write("{}\t{}\t{}\n".format("#Nodes (id", "xPos", "yPos)"))

    for i in range(res):
        f_out.write("{}\t{}\t{}\n".format(i + 1, x_pos[i], y_pos[i]))

    # Write header for connection
    f_out.write(
        "{}\t{}\t{}\t{}\t{}\t{}\n".format(
            "#Connection (nodeId1",
            "nodeId2",
            "domainId",
            "bsolver",
            "cdesolver",
            "...)",
        )
    )

    # Write connection data (all but the last connection)
    for i in range(0, res - 1):
        f_out.write("{}\t{}\t{}\n".format(i % res + 1, i % res + 2, 1))

    # add the last connection (id.res -> 1)
    f_out.write("{}\t{}\t{}\n".format(res, 1, 1))

    print("Parameters saved to {} ".format(filename))
    f_out.close()

    return None


if __name__ == "__main__":

    # Set up the parsing of command-line arguments
    parser = argparse.ArgumentParser(
        description="Write a initial round cell for LBIBCell simulation as well as the parameters"
    )
    parser.add_argument(
        "--x",
        type=int,
        default=1000,
        help="The X coordinates for center of the circle",
    )
    parser.add_argument(
        "--y",
        type=int,
        default=1000,
        help="The Y coordinates for center of the circle",
    )
    parser.add_argument(
        "-r", "--radius", type=float, default=50, help="Radius of the cell"
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="build/config",
        help="Parameters.txt and vtk files will be created",
    )
    parser.add_argument(
        "--res", type=int, default=360, help="Resolution of the circular cell"
    )
    args = parser.parse_args()

    x = args.x
    y = args.y
    radius = args.radius
    out_dir = args.out_dir
    res = args.res

    filename = "{}/parameters_{}_by_{}_radius_{}_res_{}.txt".format(
        out_dir, int(x), int(y), int(radius), res
    )

    # be sure not to remove previous file
    if os.path.exists(filename):
        print("Parameter {} exist".format(filename))
        if input("Do you want to OVERWRITE {}? [y] ".format(filename)) != "y":
            sys.exit(1)

    center = [x, y]
    write_circle_points_lbibcell(center, radius, res, filename=filename)
