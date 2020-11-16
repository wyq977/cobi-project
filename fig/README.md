# Fig

Parameters different from the [release](https://bitbucket.org/tanakas/lbibcell/src/master/) were explained below


## Starting tissue:

A thin box (300 x 1000) of cells where cells within selected regions are mark as type 2 (Shh producing).

4 regions are selected:
1. y = [0, 50] 4 cells, too few, later discarded, Center of the clusters (191.08, 36.76)
1. y = [75, 175] 43 cells, Center of the clusters (157.70, 139.18)
1. y = [0, 100] 43 cells, Center of the clusters (150.82, 61.53)
1. y = [0, 200] 117 cells, Center of the clusters (153.42, 109.96)

Later in calculation, sources are defined as distance to the center of the cluster in y-axis

## shh_iter_500_steps_10

* Cells are restricted to a box of 300 x 1000 by `BioSolverRemoveCells`
* Division cells are randomized by a normal distribution (400, 250) in `BioSolverCellDivisionRD`
* Shh production from type 2 cell: 1e-4
* Shh uptake/turnover on cell (type 1,2): 5e-3 * Shh concentration (exponentially)
* Shh decay elsewhere: 1e-3 * Shh concentration (exponentially)


Solver output are recorded every 10 iteration for 500 iteration

Figure with `init_zero`: During init., concentration of the shh was set to zero, otherwise, cell of type 2 are init. with concentration 1.0

* Color mapping was normalized logarithmically from min to max, as matplotlib LogLocator cannot handle zero well, a SHIFT of 1e-10 was added, thus the colorbar value starts from 1e-10

## shh_iter_2000_steps_50

* Cells are restricted to a box of 300 x 1000 by `BioSolverRemoveCells`
* Division cells are randomized by a normal distribution (400, 250) in `BioSolverCellDivisionRD`
* Shh production from type 2 cell: 1e-4
* Shh uptake/turnover on cell (type 1,2): 5e-3 * Shh concentration (exponentially)
* Shh decay elsewhere: 1e-3 * Shh concentration (exponentially)

Solver output are recorded every 10 iteration for 500 iteration

Similar setup as before, noted that `shh_gradient_200_out_init_zero` stops at 500 iter.

