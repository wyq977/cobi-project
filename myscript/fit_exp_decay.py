"""
fit_exp_decay

Fit the solver output from LBIBCell against exponetial decay function: $ C(x) = C_0 * \exp{\frac{-x}{\lambda}} $

Author: Yongqi Wang <wangyong@student.ethz.ch>
"""
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


# Some aux. function
def get_xy_section(mean_x, mean_y, solver_mat):
    x = np.arange(solver_mat.shape[1]) - mean_y
    # x = np.absolute(x)
    idx = x > 0
    y = solver_mat[int(mean_x), :]

    return x[idx], y[idx]


def get_xy_avg(mean_x, mean_y, solver_mat):
    x = np.arange(solver_mat.shape[1]) - mean_y
    # x = np.absolute(x)
    idx = x > 0

    y = np.mean(solver_mat, axis=0)
    return x[idx], y[idx]


def model_func(x, c0, k, b):
    # define type of function to search
    return c0 * np.exp(-k * x) + b


def fit_exp(x, y, p0=(1, 2, 1.0)):
    # p0 # starting search koefs
    popt, pcov = curve_fit(model_func, x, y, p0, maxfev=5000)
    return popt


def plot_and_fit(x, y, label, filename=None, log=False):
    fig, ax = plt.subplots()
    ax.plot(x, y, label=label)
    popt = fit_exp(x, y)
    x_fit = np.linspace(0, 1000, 250)
    y_fit = model_func(x_fit, popt[0], popt[1], popt[2])
    print("C0={:.4f}  Lambda={:.4f} b={:.4f}".format(popt[0], 1 / popt[1], popt[2]))
    fit_label = "C(x) = {:.4f} * exp(-x / {:.4f}) + {:.4f}".format(
        popt[0], 1 / popt[1], popt[2]
    )
    ax.plot(x_fit, y_fit, label=fit_label)
    if log:
        ax.set_yscale("log")
    ax.legend(loc="best")
    if filename:
        fig.savefig("{}.png".format(filename), dpi=200)
        print("Fig saved to {}.png".format(filename))