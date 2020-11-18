module load new gcc/6.3.0
module load new python/3.6.1 
module load new gcc/4.8.2 open_mpi/1.6.5 java/1.8.0_91 netcdf/4.3.2 python/3.6.1 qt/5.8.0 vtk/8.1.1
module load new gcc/4.8.2 mesa/12.0.6 paraview/5.6.0 

export DISPLAY=:99.0
export PYVISTA_OFF_SCREEN=true
export PYVISTA_USE_IPYVTK=true
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &
sleep 3

