#!/bin/bash
#title : autosubmission.sh
#description : This script will download, compile and submit jobs on Euler.
#author : Simon Tanaka
#date :20150529
#version :
#usage : sh autosubmission.sh
#notes :
#bash_version : 4.1.5(1)-release
#==============================================================================

#==============================================================================
# Change parameters here:
#==============================================================================
TIME=120:00
CORES=24
EXECUTABLE=growingturing_02
BRANCH="application/tanakas/activatedturing_2comp_A100"
SHA=# leave empty for newest
CONFIGFILE="growingturing_02_parameters.txt"
#==============================================================================
#==============================================================================

export OMP_NUM_THREADS=${CORES}
CURRDIR=${PWD##*/}
CURRPATH=${PWD}

# username for bitbucket:
USERNAME="tanakas" # for bitbucket
echo "bitbucket username: $USERNAME"

# read password:
#unset password
#prompt="bitbucket password: "
#while IFS= read -p "$prompt" -r -s -n 1 char
#do
#if [[ $char == $'\0' ]]
#then
#break
#fi
#prompt='*'
#PASSWORD+="$char"
#done
#echo

# if already downloaded, delete it:
if [ -d "${PWD}/lbibcell" ]; then
cd lbibcell
git fetch origin
git merge origin/${BRANCH}
cd ${CURRPATH}
echo "Download already existed, only updated."
else
# download software and checkout branch:
git clone https://kokicm@bitbucket.org/tanakas/lbibcell.git
cd lbibcell
git checkout -b $BRANCH origin/$BRANCH
cd ${CURRPATH}
fi

# check out specific SHA
if [ "${SHA}" != "" ]; then
cd ${CURRPATH}/lbibcell
git checkout $SHA
echo "Checked out SHA=${SHA}"
cd ${CURRPATH}/
fi
cd lbibcell
git log -1 > ${CURRPATH}/submission_info.txt
sed -i -e '$a\' ${CURRPATH}/submission_info.txt
cd ${CURRPATH}
#read -p "Press any key to continue... " -n1 -s

# build code:
mkdir ${CURRPATH}/lbibcell/build
cd ${PWD}/lbibcell/build
cmake -DCMAKE_BUILD_TYPE=Release ../
make
cd ${CURRPATH}

# change output path:
sed -i "/OutputPath:/c\OutputPath: /cluster/scratch/tanakas/$CURRDIR/output/" ${PWD}/lbibcell/build/apps/config/${CONFIGFILE}

# submit the job:
cd ${PWD}/lbibcell/build/apps/
bsub -n $CORES -W $TIME "./${EXECUTABLE} > terminalout.txt" >> ${CURRPATH}/submission_info.txt
