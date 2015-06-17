#!/bin/bash

BINDIR=$HOME/bin
HERE=`pwd`
JOINFILE=$HERE/join_video.py

mkdir -p $BINDIR
cp $JOINFILE $BINDIR/join_video
chmod +x $BINDIR/join_video

echo -e "finished install, add ${BINDIR} to your path"
export PATH=$PATH:$BINDIR
