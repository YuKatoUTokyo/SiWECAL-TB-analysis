#!/bin/bash

run=${1:-30003}
indir1="/gluster/maxi/ilc/tb2019/TB2019_06/run_30"
indir2="null"
#outdir=$indir1
outdir="./output"
mode=TDC

echo ./mergeRootFiles.py $run $indir1 $indir2 $outdir $mode
./mergeRootFiles.py $run $indir1 $indir2 $outdir $mode

echo ./build_events.py $outdir/run_${run}_merge.root -1 0
./build_events.py $outdir/run_${run}_merge.root -1 0
#./build_events.py $indir1/run_${run}_merge.root -1 0

