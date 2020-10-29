# CoBi Project

It took about 6 weeks for the rotation and 28 for the thesis, the timeline proposed
by Dagmar is [here](https://wiki-bsse.ethz.ch/display/DBSSEIBER/Precision+of+Morphogen+Gradient+Readout) and my [Progress Board](https://trello.com/b/I7HLyuhK)

## Ref Links

1. [Methods for Image Processing](https://link.springer.com/protocol/10.1007%2F978-1-4939-8772-6_4)
2. [Docker Image and shell script for LBIBCell Env by Yongqi](https://github.com/wyq977/docker_images/tree/master/lbibcell)
3. [Ongoing CI/CD Integration](https://github.com/wyq977/lbibcell)
4. [Marco script from porting imaging to LBIBCell](https://git.bsse.ethz.ch/kokicm/image-to-lbibcell)

## LBIBCell Simulation

Below is a basic compile options for the original [LBIBCell](https://tanakas.bitbucket.io/lbibcell/index.html), but there's another 
[repo](https://bitbucket.org/stopkaa/lbmcell/src/master/) where they store their
ongoing projects.


Since each run of simulation requires compile and editing on sources, the 
strategy used by the group is to make a branch for each case.

<details><summary>Compile Option on @d@bs-iber03</summary>

```bash
cd lbibcell
mkdir build
cd build
cmake -DVTK_DIR=/local0/lib/vtk-5.10 -DBoost_INCLUDE_DIR=/usr/local/iber/el6/boost_1_54_0 -DBoost_LIBRARIES=/usr/local/iber/el6/boost_1_54_0/stage/lib -DCMAKE_BUILD_TYPE=Release ../
make -j
```
</details>

## Imaging Processing Pipeline

Requirement:
1. Fiji (Java required, macOS see [this guide](https://dev.to/gabethere/installing-java-on-a-mac-using-homebrew-and-jevn-12m8))
2. Matlab

### By Matlab

After getting the data in profiles, one would get the following outputs:

```
        DVposition(um)  ch1     ch2     ch3     ch4
1       0.000   95.677  23.258  37.742  24.710
2       0.378   97.065  23.935  36.323  23.161
3       0.757   102.355 23.161  36.032  23.194
```

* Usually ch1 specifies DaPI so emitted in the analysis.
* Get DV length in every channel