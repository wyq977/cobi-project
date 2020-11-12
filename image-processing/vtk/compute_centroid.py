import numpy as np
from vtk import vtkXMLPolyDataReader
from vtk.util.numpy_support import vtk_to_numpy

# Now only works with convex polygon


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

    for i in range(nbOfCells):
        cell = polyData.GetCell(i)
        # make sure the celltype_id is correct
        nbOfPoints = cell.GetNumberOfPoints()
        is_celltype_id = True
        for i in range(nbOfPoints):
            Id = cell.GetPointIds().GetId(i)
            if cell_type.GetValue(Id) != celltype_id:
                is_celltype_id = False
                break

        if is_celltype_id:
            x, y = calculate_centeroid_np(cell)
            centroid_x.append(x)
            centroid_y.append(y)
            count += 1

    print("{} cells are type: {}".format(count, celltype_id))


center_centroid_celltype_id(1.0, "test_200_474cells.vtp")
