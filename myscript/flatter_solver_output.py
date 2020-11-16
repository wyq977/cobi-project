import os
import sys
import numpy as np
import glob
import matplotlib.pyplot as plt
from vtk import vtkXMLPolyDataReader
from vtk.util.numpy_support import vtk_to_numpy


def calculate_centeroid_np(cell):
    # conver vtk polygon cooridinates to array
    coor = vtk_to_numpy(cell.GetPoints().GetData())

    length = coor.shape[0]
    sum_x = np.sum(coor[:, 0])
    sum_y = np.sum(coor[:, 1])
    return sum_x / length, sum_y / length


def center_centroid_celltype_id(celltype_id, input_file):
    reader = vtkXMLPolyDataReader()
    reader.SetFileName(input_file)
    reader.Update()
    polyData = reader.GetOutput()
    polyDataPointData = polyData.GetPointData()
    # change only this
    cell_type = polyDataPointData.GetArray("cell_type")

    nbOfCells = polyData.GetNumberOfPolys()
    count = 0

    centroid_x, centroid_y = [], []

    tmp = []

    for i in range(nbOfCells):
        cell = polyData.GetCell(i)
        # make sure the celltype_id is correct
        nbOfPoints = cell.GetNumberOfPoints()
        is_celltype_id = True
        for i in range(nbOfPoints):
            Id = cell.GetPointIds().GetId(i)
            if cell_type.GetValue(Id) != celltype_id:
                is_celltype_id = False
                break  # to next cell if there's a single mismatch on Ids

        if not is_celltype_id:
            tmp.append(i)
            x, y = calculate_centeroid_np(cell)
            centroid_x.append(x)
            centroid_y.append(y)
            count += 1

    centeroids = np.array([centroid_x, centroid_y], dtype=np.float32)

    print("{:d} of {:d} cells are type: {:.1f}".format(count, nbOfCells, celltype_id))

    centeroids_avg = np.mean(centeroids, axis=1)

    return centeroids_avg


def read_solver_out_flat(filename, save_img=False, pic_name=None):

    try:
        f_out = open(filename, "r")
    except IOError:
        print("Output file {} cannot be opened".format(filename))
        sys.exit(1)

    arr = np.ndarray((1000, 1000), dtype=float)

    for line in f_out.readlines():
        line_list = line.rstrip("\n").split("\t")
        print(line_list)
        x = int(line_list[0])
        y = int(line_list[1])
        print(x, y)
        c = line_list[5]
        arr[x, y] = c

    f_out.close()
    filename_no_ext, _ = os.path.splitext(filename)
    np.save("{}.npy".format(filename_no_ext), arr)  # save binary file for future

    # mean along y axis, average over x = [1, 1000]
    mean = np.mean(arr, axis=1)
    if save_img:
        fig, ax = plt.subplots(1, figsize=[3, 3])
        x = np.linspace(0, 999, 1000, dtype=int)
        y = np.linspace(0, 999, 1000, dtype=int)
        X, Y = np.meshgrid(x, y)
        ax.set_axis_off()
        ax.contour(X, Y, arr)
        fig.savefig(pic_name, dpi=300)
        fig.clear()

    return mean


file_dir = [
    "../../local/input_geo_175cells",
    "../../local/input_geo_474cells",
    "../../local/input_geo_51cells",
]
source_vtp = [
    "vtk/test_100_175cells.vtp",
    "vtk/test_200_474cells.vtp",
    "vtk/test_50_21cells.vtp",
]

if not os.path.exists("source_mean.csv"):
    source_mean = np.ndarray((len(source_vtp), 2))
    for i in range(len(source_vtp)):
        source_mean[i] = center_centroid_celltype_id(1.0, source_vtp[i])

    np.savetxt("source_mean.csv", source_mean, delimiter=",")
else:
    source_mean = np.loadtxt("source_mean.csv", dtype=float, delimiter=",")

for i in range(len(file_dir)):
    dir = file_dir[i]
    mean_y = source_mean[i, 1]

    for file in glob.glob("{}/Cells_*.txt".format(dir)):
        filename, file_extension = os.path.splitext(file)
        print("Reading concentration from {}".format(file))
        out_name = os.path.join("{}_to_fit.txt".format(filename))
        pic_name = os.path.join("{}_c.png".format(filename))

        print("Saving contour plot from {}".format(pic_name))
        y = read_solver_out_flat(file, True, pic_name)
        x = np.arange(1000) - mean_y
        to_fit = np.stack((x, y), axis=1)
        print("Saving values for fitting from {}".format(out_name))
        np.savetxt(out_name, to_fit, delimiter=",", fmt=["%.18e", "%.18e"])
