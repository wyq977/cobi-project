import os
import warnings
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.axes_grid1 import make_axes_locatable, axes_size
from .settings import *

if get_os_name() == "linux":
    plt.switch_backend("Agg")


SOLVER_FN_TEMPLATE = "%06d.png"
SOLVER_DIR = "solver"
SHIFT = 1e-10


def plot_solver_matrix(
    filename,
    shift,
    vmin=None,
    vmax=None,
    figname=None,
):
    # TODO: fix LogNorm issue: now shifting by SHIFT to avoid issue with 0.0
    # TODO: ticks and label formatting for colobar
    # https://stackoverflow.com/questions/35728665/matplotlib-colorbar-tick-label-formatting
    try:
        mat = np.load(filename)
    except IOError:
        raise IOError(f'Solver output: "{filename}" cannot be opened')

    aspect = 20
    pad_fraction = 0.5
    width_to_height = mat.shape[0] / mat.shape[1]

    mat += shift

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
    # (300, 1000) interpreted as 300 rows and 1000 column
    img = ax.imshow(mat.T, norm=norm, cmap=cmap, origin="lower")
    ax.set_xlabel("X (LBM unit)")
    ax.set_ylabel("Y (LBM unit)")
    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    divider = make_axes_locatable(ax)
    width = axes_size.AxesY(ax, aspect=1.0 / aspect)
    pad = axes_size.Fraction(pad_fraction, width)
    cax = divider.append_axes("right", size=width, pad=pad)
    cbar = plt.colorbar(mappable, cax=cax)
    cbar.set_label("Shh gradient (LogNorm)")
    plt.tight_layout()

    if figname:
        plt.savefig(figname, dpi=300, transparent=False)
        plt.close(fig)


class SolverProcessor:
    def __init__(self, output_dir):
        self.directory = output_dir
        try:
            check_exists(output_dir)
        except FileNotFoundError:
            raise FileNotFoundError(
                f'"{output_dir}" does not exist. Try initilize with correct directory.'
            )

        try:
            self.solver_txt = self.verify_solver_output()
        except FileNotFoundError:
            raise FileNotFoundError(
                f'"{output_dir}" does not exist. Try initilize with correct directory.'
            )
        n_txt = len(self.get_solver_txt())
        if n_txt > 30:
            print("Dealing with {:d} files, please be patient :)")

        self.solver_directory = os.path.join(self.directory, SOLVER_DIR)
        try:
            os.makedirs(self.solver_directory, exist_ok=True)
        except:
            raise FileNotFoundError(
                f'"{self.solver_directory}" does not exist or cannot be createed.'
            )

        # uniform scale for later during plotting
        self.vmin = 0.0
        self.vmax = 0.0
        self.size_x, self.size_y = self.get_size()

    def get_solver_directory(self):
        return self.solver_directory

    def verify_solver_output(self):
        # TODO: add support for other cases of solver output like Cells_solver_100.txt
        lst = []
        for file in os.listdir(self.directory):
            if file == "log.txt":
                continue
            elif file.endswith(".txt"):
                lst.append(file)

        if len(lst) == 0:
            raise FileNotFoundError(
                f"No solver output like Cells_100.txt in {self.directory}"
            )

        print("{:d} solver output in {:s}".format(len(lst), self.directory))

        return lst

    def get_solver_txt(self):
        return [os.path.join(self.directory, f) for f in self.solver_txt]

    def get_size(self):
        # TODO: add support for other cases of solver output like Cells_solver_100.txt
        # one should always have the first solver output
        cell_0_solver = os.path.join(self.directory, "Cells_0.txt")
        last_line = readlast(cell_0_solver)
        line_list = last_line.rstrip("\n").split("\t")

        size_x = int(line_list[0]) + 1
        size_y = int(line_list[1]) + 1

        print("LB grid: {:d} X {:d}".format(size_x, size_y))
        print("txt saved to *.npy with np.ndarray ({:d}, {:d})".format(size_x, size_y))

        return size_x, size_y

    def save_npy(self):
        # TODO: prevent repeat loading files while getting vmin, vmax
        mat = np.zeros((self.size_x, self.size_y), dtype=float)

        for f in self.get_solver_txt():
            filename, _ = os.path.splitext(f)
            npy = "{}.npy".format(filename)

            try:
                f_out = open(f, "r")
            except IOError:
                raise IOError(f'"{f}" does not exist or cannot be createed.')

            for line in f_out.readlines():
                line_list = line.rstrip("\n").split("\t")
                x = int(line_list[0])
                y = int(line_list[1])
                c = float(line_list[5])
                mat[x, y] = c

                # uniform scale for later during plotting
                if self.vmin > c:
                    self.vmin = c
                if self.vmax < c:
                    self.vmax = c

            f_out.close()

            np.save(npy, mat)
            print(f'\rtxt saved as "{filename}".npy...', end="")

        self.vmax += SHIFT
        self.vmin += SHIFT
        print()

    def plot_solver(self, vmin=None, vmax=None):
        SHIFT_TMP = 0.0  # no shifting when providing range
        if not vmin and not vmax:
            vmin = self.vmin
            vmax = self.vmax
            warning(
                f"colorbar shifted by {SHIFT} now"
                f" This means value displayed on colorbar should be deducted by {SHIFT}"
                " Caused by matplotlib.colors.LogNorm",
                UserWarning,
                stacklevel=2,
            )
            SHIFT_TMP = SHIFT

        for f in self.solver_txt:
            filename, _ = os.path.splitext(f)
            npy = os.path.join(self.directory, "{}.npy".format(filename))
            figname = os.path.join(
                self.get_solver_directory(), "{}.png".format(filename)
            )

            plot_solver_matrix(npy, SHIFT_TMP, vmin, vmax, figname)
            print(f"\rPlotting {figname}...", end="")

        print()