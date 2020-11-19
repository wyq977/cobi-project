import argparse
from myscript.report_processor.solver_processor import SolverProcessor

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