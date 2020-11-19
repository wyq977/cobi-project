import os
import sys
import argparse
import numpy as np

from vtk import vtkXMLPolyDataReader, vtkPoints, vtkXMLPolyDataWriter
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk


def move_vtp_along(input_file, output_filename, x_dist):
    reader = vtkXMLPolyDataReader()
    reader.SetFileName(input_file)
    reader.Update()
    polyData = reader.GetOutput()

    coor = vtk_to_numpy(polyData.GetPoints().GetData())
    coor[:, 0] += x_dist

    points = vtkPoints()
    points.SetData(numpy_to_vtk(coor, deep=True))
    polyData.SetPoints(points)

    print("{} moved {} in x direction".format(input_file, x_dist))
    print("Saved to {}".format(output_filename))
    writer = vtkXMLPolyDataWriter()
    writer.SetFileName(output_filename)
    writer.SetInputData(polyData)
    writer.SetDataModeToAscii()
    writer.Write()


if __name__ == "__main__":

    # Set up the parsing of command-line arguments
    parser = argparse.ArgumentParser(
        description="Move a vtp along x-axis",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("-i", "--input", type=str)
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument(
        "-x", "--x_dist", type=int, default=-350, help="Distance to be moved in x axis"
    )
    args = parser.parse_args()

    filename = args.input
    out = args.output
    _, ext = os.path.splitext(filename)

    # be sure not to remove previous file and check input valid
    if not os.path.exists(filename) or ext != ".vtp":
        print(
            "{} not valid, should be a vtp file, i.e. Cells_4000_0.vtp".format(filename)
        )
        sys.exit(1)
    elif os.path.exists(out):
        print("{} exist".format(out))
        if input("Do you want to OVERWRITE {}? [y] ".format(out)) != "y":
            sys.exit(1)

    move_vtp_along(filename, out, args.x_dist)
