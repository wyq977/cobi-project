import os
import sys
import argparse
import matplotlib.pyplot as plt

# from matplotlib.pyplot import show
from numpy import mean
import pandas as pd
import numpy as np
from scipy.stats import variation, gstd
from skimage import color, filters, measure, morphology, segmentation, io

params = {
    "legend.fontsize": "x-small",
    "axes.labelsize": "x-small",
    "axes.titlesize": "x-small",
    "xtick.labelsize": "x-small",
    "ytick.labelsize": "x-small",
    # "font.family": "serif",
    # "font.serif": ['Times'],
    # "font.sans-serif": ["Helvetica"],
    # 'font.family' : 'sans-serif',
    # 'text.usetex': True,
    # 'font.serif': 'Helvetica'
}
plt.rcParams.update(params)


def seg_lbibcell(filename, outdir, size_x, size_y, show=False):
    """Segmentate Cells after simulation and compute corresponding stats.

    Parameters
    ----------
    filename : str
        Path to the screenshot or microscropy image
    outdir : str
        Path to save the plot and statistics about segmentated cells
    size_x : int
        The X-axis for the box grid, i.e. 1000
    size_y : int
        The Y-axis for the box grid, i.e. 1000
    show : bool
        To show the img or not, by default False
    """
    if outdir:
        try:
            os.makedirs(outdir)
        except FileExistsError:
            print("{} already exists!".format(outdir))
            if input("Do you want to OVERWRITE {}? [y] ".format(filename)) != "y":
                sys.exit(1)

    # read img as greyscale
    img = io.imread(filename, as_gray=True)
    print("Input: {} X {}".format(img.shape[0], img.shape[1]))

    # scale factor size the simulation takes place in a fixed box grid
    SCALE_X = img.shape[0] / size_x
    SCALE_Y = img.shape[1] / size_y
    AREA_SCALE = SCALE_X * SCALE_Y
    SMALL_OBJECTS_THRESHOLD = 40

    # Use Multi-Otsu Thresholding
    thresholds = filters.threshold_multiotsu(img, classes=2)

    # get label cells, background is darker
    cells = img < thresholds

    # remove objects < 40, have to remove small artifacts
    cells_clean = morphology.remove_small_objects(
        cells, SMALL_OBJECTS_THRESHOLD * AREA_SCALE
    )

    labeled_cells_threshold_multiotsu = measure.label(cells_clean)

    region_props = ["label", "area", "centroid"]
    props = measure.regionprops_table(
        labeled_cells_threshold_multiotsu, img, properties=region_props
    )

    # rescale
    props["area"] = props["area"] / AREA_SCALE
    props["centroid-0"] = props["centroid-0"] / SCALE_X
    props["centroid-1"] = props["centroid-1"] / SCALE_Y

    image_label_overlay = color.label2rgb(
        labeled_cells_threshold_multiotsu, image=img, bg_label=0
    )

    print(
        "{} cells identified from the image".format(
            labeled_cells_threshold_multiotsu.max()
        )
    )  # nopep8
    print(
        "Average area : {:.4f} +/- {:.2f}".format(
            mean(props["area"]), gstd(props["area"])
        )
    )  # nopep8
    print("CV           : {:.4f}".format(variation(props["area"])))
    print("min          : {:.4f}".format(np.min(props["area"])))
    print("max          : {:.4f}".format(np.max(props["area"])))

    fig, axes = plt.subplots(2, 2, figsize=(4, 4))  # , constrained_layout=True
    ax = axes.ravel()

    ax[0].imshow(io.imread(filename))
    ax[0].set_title("Original Image")
    ax[0].set_axis_off()

    ax[1].imshow(segmentation.mark_boundaries(img, labeled_cells_threshold_multiotsu))
    ax[1].set_title(
        "Multi-Otsu Thresholding (< {} removed)".format(SMALL_OBJECTS_THRESHOLD)
    )
    ax[1].set_axis_off()

    ax[2].scatter(
        x=props["centroid-0"], y=props["centroid-1"], s=props["area"] / (size_x * 20)
    )
    ax[2].set_title("Centroid of cells")
    ax[2].set_axis_off()

    ax[3].imshow(image_label_overlay)
    ax[3].set_title("Labelled cells (Color)")
    ax[3].set_axis_off()

    if show:
        plt.show()
    if outdir:
        fig.set_size_inches(12, 12)
        fig.savefig(outdir + "/segmentated_img.pdf", dpi=300)
        print("Segmentated image saved to {}/segmentated_img.pdf".format(outdir))

        # turns a dict to df for easy export
        props = pd.DataFrame(props)
        props.to_csv(outdir + "/segmentated_res.csv")
        print("Have been saved to {}/segmentated_res.csv".format(outdir))

    plt.close()


if __name__ == "__main__":

    # Set up the parsing of command-line arguments
    parser = argparse.ArgumentParser(
        prog="seg_lbibcell", description="Segementate image of cell after LBIBCell"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=str,
        required=True,
        help="Image saved from Paraview, i.e. screenshot.png",
    )
    parser.add_argument(
        "--outdir",
        type=str,
        help="Diretory to create plots and save statistics about the cell",
    )
    parser.add_argument(
        "-x",
        "--SizeX",
        type=int,
        default=1000,
        help="The X-axis for the box grid, i.e. 1000, by default 1000",
    )
    parser.add_argument(
        "-y",
        "--SizeY",
        type=int,
        default=1000,
        help="The Y-axis for the box grid, i.e. 1000, by default 1000",
    )
    parser.add_argument(
        "--show", default=False, action="store_true", help="Show the image"
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1")
    args = parser.parse_args()

    seg_lbibcell(args.input, args.outdir, args.SizeX, args.SizeY, args.show)
