#!/bin/bash

BINDIR=$HOME/bin
HERE=`pwd`
JOINFILE=(join_video.py transfer_video.py)

mkdir -p $BINDIR

for file in ${JOINFILE[*]}; do
  cp $HERE/$file $BINDIR/$file
  chmod +x $BINDIR/$file
done

echo -e "finished install, add ${BINDIR} to your path"
export PATH=$PATH:$BINDIR
