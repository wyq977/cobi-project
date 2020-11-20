import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


def shh_readout_anl_sol_inf_cf(x, p, d, Lf, Lt, k):
    # k is the inverse of lambda
    return p / d * (1 - np.exp(-Lf * k) * np.cosh(x * k))


def shh_readout_anl_sol_inf_cp(x, p, d, Lf, Lt, k):
    # k is the inverse of lambda
    return p / d * np.sinh(Lf * k) * np.exp(-x * k)


def shh_read_out_analytic_sol_inf(x, p, d, Lf, Lt, k):
    res = np.zeros_like(x)
    cf_idx = x <= Lf
    cp_idx = x > Lf
    res[cf_idx] = shh_readout_anl_sol_inf_cf(x[cf_idx], p, d, Lf, Lt, k)
    res[cp_idx] = shh_readout_anl_sol_inf_cp(x[cp_idx], p, d, Lf, Lt, k)

    return res


def shh_readout_anl_sol_cf(x, p, d, Lf, Lt, k):
    # k is the inverse of lambda
    return p / d * (1 + np.sinh((Lf - Lt) * k) / np.sinh(Lt * k) * np.cosh(x * k))


def shh_readout_anl_sol_cp(x, p, d, Lf, Lt, k):
    # k is the inverse of lambda
    return p / d * np.sinh(Lf * k) / np.sinh(Lt * k) * np.cosh((Lt - x) * k)


def shh_read_out_analytic_sol(x, p, d, Lf, Lt, k):
    res = np.zeros_like(x)
    cf_idx = x <= Lf
    cp_idx = x > Lf
    res[cf_idx] = shh_readout_anl_sol_cf(x[cf_idx], p, d, Lf, Lt, k)
    res[cp_idx] = shh_readout_anl_sol_cp(x[cp_idx], p, d, Lf, Lt, k)

    return res


def model_func(x, c0, k, b):
    # define type of function to search
    return c0 * np.exp(-k * x) + b


def fit_exp(x, y, p0=(1, 2, 1.0)):
    # p0 # starting search koefs
    popt, pcov = curve_fit(model_func, x, y, p0, maxfev=5000)
    return popt


def plot_and_fit(x, y, label, show=False, filename=None, log=False, anl_param=None):
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

    if show:
        fig.show()
