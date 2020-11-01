## Process of the Simulation in LBIBCell

* What is the boundaryNode? what is the neibours to that?
* What is Geometry doing?

* In LBIBCell:
  * physicalNode is the node in grid point with: `force, velocity, distribute, sd`, has 9 neibouring physical node (similar to D2Q9)
  * geometry, 16 neighbourPhysicalNodes,  neibour is the node in grid point with: `force, velocity, distribute, sd`, has 9 neibouring physical node


1. First the force on geometryNode were calculated, see ForceStructs and the force.txt

2. **distributeForce** `distributeForce`: distribute force on all **geometry**
   1. Force of all physical node in lattice are reset to (0,0)
   2. Of 16 neighbourPhysicalNodes of every geometryNode, every one is added with a force using calculateDiscreteDeltaDirac based on the distance `physicalNode -> geometryNode`
   3. HOW to set up a
   
3. **Advection**

   1. **preAdvection** on every **boundaryNode** and **boundarySolver**

      Basically for every boundaryNode, 

      and every boundarySolver on that, do a preAdvect

   2. **advection** on every **physicalNode** and **boundaryNode**

      1. For every physicalNode, get `fluidSolver().advect`
      2. For every CDESolver on it, do advect 

   3. **postAdevtion** on **boundaryNode**

      1. Basically for every boundaryNode, 
      2. and every boundarySolver on that, do a postAdvect

4. **collide** on every **physicalNode** all the CDESolver and fluidSolver

   1. For every physicalNode,
   2. fluidSolver collide()
   3. CDESolver collide()

5. **collectVelocity** on every **geometryNode**

   1. each geometry node collect velocity
   2. look into details to help understand the

6. **moveGeometry** `moveLattice` by the handler

7. **remeshBoundary** `remeshBoundary`





