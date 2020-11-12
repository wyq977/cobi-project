"""
fit_exp_decay

Fit the solver output from LBIBCell against exponetial decay function: $ C(x) = C_0 * \exp{\frac{-x}{\lambda}} $

Author: Yongqi Wang <wangyong@student.ethz.ch>
"""
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def model_func(x, c0, k):
    # define type of function to search
    return c0 * np.exp(-k * x)


def fit_exp(x, y, p0=(1000, 2)):
    # p0 # starting search koefs
    popt, pcov = curve_fit(model_func, x, y, p0, maxfev=5000)
    return popt


if __name__ == "__main__":
    source_mean = np.loadtxt("source_mean.csv", dtype=float, delimiter=",")
    iteration = 300
    # print(source_mean[0])
    to_fit_0 = np.loadtxt(
        "../../local/input_geo_175cells/Cells_{}_to_fit.txt".format(iteration),
        dtype=float,
        delimiter=",",
    )
    to_fit_1 = np.loadtxt(
        "../../local/input_geo_474cells/Cells_{}_to_fit.txt".format(iteration),
        dtype=float,
        delimiter=",",
    )
    to_fit_2 = np.loadtxt(
        "../../local/input_geo_51cells/Cells_{}_to_fit.txt".format(iteration),
        dtype=float,
        delimiter=",",
    )
    # to_fit_3 = np.load('../../local/input_geo_51cells/Cells_100.npy')
    # to_fit_3 = to_fit_3[500, :]

    # popt = fit_exp(to_fit_0[:,0], to_fit_0[:,1])
    # c0, k = popt
    # x2 = np.linspace(0, 1000, 250)
    # y2 = model_func(x2, c0, k)
    fig, ax = plt.subplots()
    # fig, ax = plt.subplots(ncols=3, figsize=[12, 4])
    # ax.plot(x2, y2, label='Fit. func: $f(x) = %.3f e^{%.3f x}$' % (c0,k))

    # ax.plot(to_fit_0[:,0][to_fit_0[:,0] > 0] + source_mean[0][1], to_fit_0[:,1][to_fit[:,0] > 0], 'r', label='box 100 175 cells', alpha=0.5)
    # ax.plot(to_fit_1[:,0][to_fit_1[:,0] > 0] + source_mean[1][1], to_fit_1[:,1][to_fit_1[:,0] > 0], 'b', label='box 200 474 cells', alpha=0.5)
    # ax.plot(to_fit_2[:,0][to_fit_2[:,0] > 0] + source_mean[2][1], to_fit_2[:,1][to_fit_2[:,0] > 0], 'y', label='box  50 21 cells', alpha=0.5)
    ax.plot(
        to_fit_0[:, 0][to_fit_0[:, 0] > 0],
        to_fit_0[:, 1][to_fit_0[:, 0] > 0],
        "r",
        label="box 100 175 cells",
    )
    ax.plot(
        to_fit_1[:, 0][to_fit_1[:, 0] > 0],
        to_fit_1[:, 1][to_fit_1[:, 0] > 0],
        "b",
        label="box 200 474 cells",
    )
    ax.plot(
        to_fit_2[:, 0][to_fit_2[:, 0] > 0],
        to_fit_2[:, 1][to_fit_2[:, 0] > 0],
        "y",
        label="box  50 21  cells",
    )
    ax.set_xlabel("Distance from source (LB units)")
    ax.set_ylabel("Morphogen concentraction")
    ax.set_title("Average concentraction vs distance at iter. {}".format(iteration))
    # ax.plot(to_fit_1[:,0], to_fit_3, label='Not average')
    ax.legend(loc="best")
    # ax[0].plot(to_fit[:,0], to_fit[:,1], label='box 100 175 cells')
    # ax[0].legend(loc='best')

    # ax[1].plot(to_fit_1[:,0], to_fit_1[:,1], label='box 200 474 cells')
    # ax[1].legend(loc='best')

    # ax[2].plot(to_fit_2[:,0], to_fit_2[:,1], label='box  50 21 cells')
    # ax[2].legend(loc='best')

    fig.savefig("{}.png".format(iteration), dpi=300)

    fig, ax = plt.subplots(ncols=3, figsize=[12, 4])

    image = plt.imread("vtk/test_50_21cells.png")
    ax[0].imshow(image)
    ax[0].axis("off")
    ax[0].set_title("box  50 21  cells")

    image = plt.imread("vtk/test_100_175cells.png")
    ax[1].imshow(image)
    ax[1].axis("off")
    ax[1].set_title("box 100 175 cells")

    image = plt.imread("vtk/test_200_474cells.png")
    ax[2].imshow(image)
    ax[2].axis("off")
    ax[2].set_title("box 200 474 cells")

    fig.savefig("floor_plate.png", dpi=300)
