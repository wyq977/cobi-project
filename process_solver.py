import argparse
from myscript.report_processor.solver_processor import SolverProcessor
from myscript.report_processor.solver_processor import get_solver_mat
import os

if __name__ == "__main__":

    # Set up the parsing of command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input_dir",
        type=str,
        required=True,
        help="LBIBCell reporter output dir",
    )
    args = parser.parse_args()

    solver_processor = SolverProcessor(args.input_dir)

    solver_processor.save_npy()

    solver_processor.plot_solver()

    solver_processor.png_to_gif()

    # mat = solver_processor.get_solver_mat("Cells_100.txt")
    # print(mat.shape)

    # mat = get_solver_mat(os.path.join(args.input_dir, "Cells_100.txt"), flatten=1)
    # print(mat.shape)
