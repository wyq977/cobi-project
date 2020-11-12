import os
import sys
from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.animation as animation
import numpy as np
from glob import glob
from vtk import vtkXMLPolyDataReader
from vtk.util.numpy_support import vtk_to_numpy
import shutil

fig, ax = plt.subplots(figsize=(6, 1))
fig.subplots_adjust(bottom=0.5)

cmap = mpl.cm.cool
norm = mpl.colors.Normalize(vmin=5, vmax=10)

cb1 = mpl.colorbar.ColorbarBase(ax, cmap=cmap, norm=norm, orientation="horizontal")
cb1.set_label("Some Units")
fig.show()

BOX_SIZE = [50, 100, 200]
INIT_CONCENTRATION = ["", "_init_zero"]

file_dir = []
solver_output_list = []
cell_type_vtp_list = []
solver_mat_list = []

for box in BOX_SIZE:
    for init in INIT_CONCENTRATION:
        dir = "../../local/shh_gradient_{:d}_out{:s}".format(box, init)
        file_dir.append(dir)
        for solver_output in glob("{:s}/Cells_*.txt".format(dir)):
            cells_idx, _ = os.path.splitext(os.path.basename(solver_output))
            # print(cells_idx)
            solver_output_list.append(solver_output)
            cell_type_vtp_list.append(
                "{:s}/{:s}/{:s}_0.vtp".format(dir, cells_idx, cells_idx)
            )
            solver_mat_list.append("{:s}/{:s}.npy".format(dir, cells_idx))

assert len(solver_output_list) == len(cell_type_vtp_list)


def save_solver_as_mat(filename, size_x=300, size_y=1000):
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


def calculate_centeroid_np(cell):
    # conver vtk polygon cooridinates to array
    # now its trivial for convex polygon
    # TODO: use vtk in-house method
    coor = vtk_to_numpy(cell.GetPoints().GetData())

    length = coor.shape[0]
    sum_x = np.sum(coor[:, 0])
    sum_y = np.sum(coor[:, 1])
    return sum_x / length, sum_y / length


def save_centroid_celltype_id_np(celltype_id, filename):
    reader = vtkXMLPolyDataReader()
    reader.SetFileName(filename)
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

        if is_celltype_id:
            tmp.append(i)
            x, y = calculate_centeroid_np(cell)
            centroid_x.append(x)
            centroid_y.append(y)
            count += 1

    print("{:d} of {:d} cells are type: {:.1f}".format(count, nbOfCells, celltype_id))
    if count > 0:
        centeroids = np.array([centroid_x, centroid_y], dtype=np.float32)
        filename_no_ext, _ = os.path.splitext(filename)
        print("Saving to {}.npy".format(filename_no_ext))
        np.save(
            "{}.npy".format(filename_no_ext), centeroids
        )  # save binary file for future
    else:
        print("No cells of type {:.1f}".format(celltype_id))


# https://stackoverflow.com/questions/16915966/using-matplotlib-animate-to-animate-a-contour-plot-in-python
# https://stackoverflow.com/questions/32455162/how-to-plot-contourf-colorbar-in-different-subplot-matplotlib
# Generate grid for plotting


def draw_contourf(dir, steps=10):
    # consistent max
    vmin, vmax = 0.0, 0.0
    count = 0
    for solver_npy in glob("{:s}/Cells_*.npy".format(dir)):
        mat = np.load(solver_npy)
        mat_min = np.min(mat)
        mat_max = np.max(mat)
        if vmin > mat_min:
            vmin = mat_min
        if vmax <= mat_max:
            vmax = mat_max

        count += 1

    x = np.linspace(0, 299, 300, dtype=int)
    y = np.linspace(0, 999, 1000, dtype=int)
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
    cbar.set_label("Shh con.")

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


def convert_mp4_gif(dir):
    fig_dir = "{:s}/fig".format(dir)

    print("Converting contourf into vid and gif")

    convert_vid = "ffmpeg -loglevel panic -y -f image2 -framerate 10 -i {}/contourf_%d.png {}/contourf.mp4".format(
        fig_dir, fig_dir
    )
    # convert_gif_palette='ffmpeg -loglevel panic -i {}/contourf.mp4 -vf "palettegen" -y /tmp/palette.png'.format(fig_dir)
    # convert_gif = 'ffmpeg -loglevel panic -y -i {}/contourf.mp4 -i /tmp/palette.png -lavfi "fps=10 [x]; [x][1:v] paletteuse" {}/contourf.gif'.format(fig_dir, fig_dir)
    # convert_gif = 'ffmpeg -loglevel panic -y -i {}/contourf.mp4 {}/contourf.gif'.format(fig_dir, fig_dir)
    convert_gif = (
        "gifski --fps 10 --width 1500 -o {}/contourf.gif {}/contourf.mp4".format(
            fig_dir, fig_dir
        )
    )

    try:
        if os.system(convert_vid) != 0:
            print("mp4 are not converted")
        if os.system(convert_gif) != 0:
            # if os.system(convert_gif_palette) != 0 and os.system(convert_gif) != 0:
            print("gif are not converted")
    except:
        print("ffmpeg convert does not work")


for box in BOX_SIZE:
    for init in INIT_CONCENTRATION:
        dir = "../../local/shh_gradient_{:d}_out{:s}".format(box, init)
        draw_contourf(dir, steps=50)
        convert_mp4_gif(dir)
        try:
            shutil.copy(
                "{}/fig/contourf.mp4".format(dir),
                "./shh_gradient_{:d}_out{:s}_contourf.mp4".format(box, init),
            )
            shutil.copy(
                "{}/fig/contourf.gif".format(dir),
                "./shh_gradient_{:d}_out{:s}_contourf.gif".format(box, init),
            )
        except:
            print("Copying error")
