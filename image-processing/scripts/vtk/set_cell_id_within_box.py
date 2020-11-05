"""
set_cell_id_within_box

Change the cells within a box limit, input vtp should follow vtkCellReporter

Author: Yongqi Wang <wangyong@student.ethz.ch>
"""
#
# add numpy support for calculation
import os
import sys
import argparse
import numpy as np
from vtk import vtkXMLPolyDataReader, vtkXMLPolyDataWriter
from vtk.util.numpy_support import vtk_to_numpy
arg_log = """
Example: python3 set_cell_id_within_box.py -i Cells_1000_0.vtp --id 2 --box 0 0 200 200 -o Cells_1000_0_cell_id_mod.vtp

The input should follow the format described in the reporter vtkCellReporter in
LBIBCell. Since the Points are stored as Float32 and ascii, there will be some
errors in that section of xml.

Dealing with vtk in python is quite a mess, so I decide to convert the spatial
cooridnates into numpy array from easy extraction of coordinates data.

See here for more on conversion:
https://stackoverflow.com/questions/49187430/strange-vtk-results-on-the-computation-of-surface-cell-areas-using-python

DISCLAIMERS:
Only tested on macos with vtk 9.0.1 installed from conda-forge
"""


def is_cell_within_box(cell,
                       MIN_X,
                       MIN_Y,
                       MAX_X,
                       MAX_Y,
                       debug=False,
                       lattice_x=1005,
                       lattice_y=1005):
    """Take a cell (vtk Polygon) and see if it's within a box limit

    Parameters
    ----------
    cell : vtkPolygon
        Must be a valid cell, otherwise crashes
    MIN_X : float
        Min limit for X
    MIN_Y : float
        Min limit for Y
    MAX_X : float
        Max limit for X
    MAX_Y : float
        Max limit for Y
    debug : bool, optional
        Whether to show the text and img, by default False
    lattice_x : int, optional
        The size of lattice in LBM, by default 1005
    lattice_y : int, optional
        The size of lattice in LBM, by default 1005

    Returns
    -------
    Bool
        Wether the cell is within the limit imposed
    """

    # conver vtk polygon cooridinates to array
    coor = vtk_to_numpy(cell.GetPoints().GetData())
    min_x = np.min(coor[:, 0])
    max_x = np.max(coor[:, 0])
    min_y = np.min(coor[:, 1])
    max_y = np.max(coor[:, 1])

    is_within = (min_x > MIN_X and min_y > MIN_Y and max_x < MAX_X
                 and max_y < MAX_Y)

    if debug:
        print('x: [{:.2f} - {:.2f}]'.format(min_x, max_x))
        print('y: [{:.2f} - {:.2f}]'.format(min_y, max_y))
        if is_within: print('Cell is within the box limit')
        else: print('!!! Cell is NOT within the box limit')
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            # Create figure and axes
            fig, ax = plt.subplots(1, figsize=[3, 3])
            ax.set_ylim(0, lattice_x)
            ax.set_xlim(0, lattice_y)
            ax.set_axis_off()
            # Create a Rectangle patch
            cell = patches.Rectangle((min_x, min_y), (max_x - min_x),
                                     (max_y - min_y),
                                     linewidth=2,
                                     edgecolor='r',
                                     facecolor='none')
            limit = patches.Rectangle((MIN_X, MIN_Y), (MAX_X - MIN_X),
                                      (MAX_Y - MIN_Y),
                                      linewidth=2,
                                      edgecolor='b',
                                      facecolor='none')
            ax.add_patch(cell)
            ax.add_patch(limit)
            fig.show()
        except ImportError:
            print('No ploting')
            pass

    return is_within


def write_celltype_id(box,
                      celltype_id,
                      input_file,
                      output_filename,
                      lattice_x=1005,
                      lattice_y=1005):
    MIN_X, MIN_Y, MAX_X, MAX_Y = box
    reader = vtkXMLPolyDataReader()
    reader.SetFileName(input_file)
    reader.Update()
    polyData = reader.GetOutput()
    polyDataPointData = polyData.GetPointData()
    # change only this
    cell_type = polyDataPointData.GetArray('cell_type')

    nbOfCells = polyData.GetNumberOfPolys()
    count = 0

    for i in range(nbOfCells):
        cell = polyData.GetCell(i)
        if is_cell_within_box(cell, MIN_X, MIN_Y, MAX_X, MAX_Y, False,
                              lattice_x, lattice_y):
            # need to iter. thr. all Points of that polygon
            nbOfPoints = cell.GetNumberOfPoints()
            for i in range(nbOfPoints):
                Id = cell.GetPointIds().GetId(i)
                cell_type.SetValue(Id, celltype_id)
            count += 1

    print('{} cells are within the box limit'.format(count))
    print('Cell type id changed to {}'.format(celltype_id))
    writer = vtkXMLPolyDataWriter()
    writer.SetFileName(output_filename)
    writer.SetInputData(polyData)
    writer.SetDataModeToAscii()
    writer.Write()


if __name__ == '__main__':

    # Set up the parsing of command-line arguments
    parser = argparse.ArgumentParser(
        description=
        "Write a initial round cell for LBIBCell simulation as well as the parameters",
        epilog=arg_log,
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-i",
                        "--input",
                        type=str,
                        help="Input file from LBIBCell")
    parser.add_argument("--id",
                        type=int,
                        default=2,
                        help="Celltype ID changed")
    parser.add_argument("-x",
                        "--SizeX",
                        type=int,
                        default=1000,
                        help="The X-axis for the box grid, i.e. 1000")
    parser.add_argument("-y",
                        "--SizeY",
                        type=int,
                        default=1000,
                        help="The Y-axis for the box grid, i.e. 1000")
    parser.add_argument("--box",
                        type=float,
                        nargs="+",
                        required=True,
                        help="The box limit, i.e. MIN_X, MIN_Y, MAX_X, MAX_Y")
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        help="Ouput filename, i.e. Cells_4000_0_cell_id_mod.vtp")
    args = parser.parse_args()

    filename = args.input
    id = args.id
    size_x = args.SizeX + 5
    size_y = args.SizeY + 5
    box = args.box
    output_file = args.output_file
    filename_no_ext, ext = os.path.splitext(filename)

    if not output_file:
        output_file = "{}_cell_id_mod.vtp".format(filename_no_ext)

    # be sure not to remove previous file and check input valid
    if not os.path.exists(filename) or ext != '.vtp':
        print(
            '{} not valid, should be a vtp file, i.e. Cells_4000_0.vtp'.format(
                filename))
        sys.exit(1)
    elif len(box) != 4 or box[0] > box[2] or box[1] > box[3]:
        print('Input box dim not valid i.e. --box 1 25 100 150')
        sys.exit(1)
    elif os.path.exists(output_file):
        print("{} exist".format(output_file))
        if input('Do you want to OVERWRITE {}? [y] '.format(
                output_file)) != 'y':
            sys.exit(1)

    write_celltype_id(box, id, filename, output_file, size_x, size_y)
