"""
fit_exp_decay

Fit the solver output from LBIBCell against exponetial decay function: $ C(x) = C_0 * \exp{\frac{-x}{\lambda}} $

Author: Yongqi Wang <wangyong@student.ethz.ch>
"""
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def shh_read_out_analytic_sol_inf(x, p, d, Lf, Lt, k):
    # k is the inverse of lambda
    assert x >= 0 and x <= Lt
    readout = 0
    if x <= Lf:
        readout = p / d * (1 - np.exp(-Lf * k) * np.cosh(x * k))
    else:
        readout = p / d * np.sinh(Lf * k) * np.exp(-x * k)
    return readout


def shh_read_out_analytic_sol(x, p, d, Lf, Lt, k):
    # k is the inverse of lambda
    assert x >= 0 and x <= Lt
    readout = 0
    if x <= Lf:
        readout = (
            p / d * (1 + np.sinh((Lf - Lt) * k) / np.sinh(Lt * k) * np.cosh(x * k))
        )
    else:
        readout = p / d * np.sinh(Lf * k) / np.sinh(Lt * k) * np.cosh((Lt - x) * k)
    return readout


# Some aux. function
def get_xy_section(mean_x, mean_y, solver_mat):
    x = np.arange(solver_mat.shape[1]) - mean_y
    # x = np.absolute(x)
    idx = x > 0
    y = solver_mat[int(mean_x), :]

    return x[idx], y[idx]
    # return x, y


def get_xy_avg(mean_x, mean_y, solver_mat):
    x = np.arange(solver_mat.shape[1]) - mean_y
    # x = np.absolute(x)
    idx = x > 0

    y = np.mean(solver_mat, axis=0)
    return x[idx], y[idx]
    # return x, y


def model_func(x, c0, k, b):
    # define type of function to search
    return c0 * np.exp(-k * x) + b


def fit_exp(x, y, p0=(1, 2, 1.0)):
    # p0 # starting search koefs
    popt, pcov = curve_fit(model_func, x, y, p0, maxfev=5000)
    return popt


def plot_and_fit(x, y, label, filename=None, log=False, anl_param=None):
    fig, ax = plt.subplots()
    ax.scatter(x, y, label=label, s=2.4, alpha=0.9, c="lightsteelblue")
    popt = fit_exp(x, y)
    x_fit = np.linspace(0, 1000, 250)
    y_fit = model_func(x_fit, popt[0], popt[1], popt[2])
    print("C0={:.4f}  Lambda={:.4f} b={:.4f}".format(popt[0], 1 / popt[1], popt[2]))
    fit_label = "C(x) = {:.4f} * exp(-x / {:.4f}) + {:.4f}".format(
        popt[0], 1 / popt[1], popt[2]
    )
    ax.plot(x_fit, y_fit, label=fit_label, c="darkorange")
    if log:
        ax.set_yscale("log")

    if anl_param:
        y_anl = np.zeros_like(x_fit)
        p, d, Lf, Lt = anl_param
        k = popt[1]
        for i in range(x_fit.shape[0]):
            y_anl[i] = shh_read_out_analytic_sol_inf(x_fit[i], p, d, Lf, Lt, k)

        ax.plot(x_fit, y_anl, label="Analtic solution", c="seagreen", linestyle="--")

    ax.legend(loc="best")
    if filename:
        fig.savefig("{}.png".format(filename), dpi=200)
        print("Fig saved to {}.png".format(filename))
