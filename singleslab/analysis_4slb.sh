#!/bin/bash
#Expect files in this format:
# /path/run_XXXXX_SLB_2.root (or SLB_3)
# run example:
#> source analysis.sh XXXXX convert
# where:
#          XXXXX is the run number
#          convert=0 if no conversiom =1 if yes

#source analysis.sh 21010 1

run=$1
convert=$2

data_folder= "/home/calice/TB201906/SLB_data/"
if (( $convert == 1));
then
    for path in ../../SLB_data/run_"${run}"*i
    do
	echo $path
	root -l ../converter_SLB/ConvertDirectorySL.cc\(\"${path}/\",0,4\) &
        root -l ../converter_SLB/ConvertDirectorySL.cc\(\"${path}/\",1,4\)  
	root -l ../converter_SLB/ConvertDirectorySL.cc\(\"${path}/\",2,4\) &
	root -l ../converter_SLB/ConvertDirectorySL.cc\(\"${path}/\",3,4\)
	sleep 30
    done
    
    if ( ls ${data_folder}/run_${run}*/*dat_0*SLB_2.root )
    then
	echo "more than one file "
	hadd -f ${data_folder}/run_${run}_SLB_0.root ${data_folder}/run_${run}*/*dat_SLB_0.root ${data_folder}/run_${run}*/*dat_0*SLB_0.root &
	hadd -f ${data_folder}/run_${run}_SLB_1.root ${data_folder}/run_${run}*/*dat_SLB_1.root ${data_folder}/run_${run}*/*dat_0*SLB_1.root 
	hadd -f ${data_folder}/run_${run}_SLB_2.root ${data_folder}/run_${run}*/*dat_SLB_2.root ${data_folder}/run_${run}*/*dat_0*SLB_2.root &
	hadd -f ${data_folder}/run_${run}_SLB_3.root ${data_folder}/run_${run}*/*dat_SLB_3.root ${data_folder}/run_${run}*/*dat_0*SLB_3.root
	sleep 20
    else
	echo "only one file "
	hadd -f ${data_folder}/run_${run}_SLB_0.root ${data_folder}/run_${run}*/*dat_SLB_0.root &
	hadd -f ${data_folder}/run_${run}_SLB_1.root ${data_folder}/run_${run}*/*dat_SLB_1.root &
	hadd -f ${data_folder}/run_${run}_SLB_2.root ${data_folder}/run_${run}*/*dat_SLB_2.root &
	hadd -f ${data_folder}/run_${run}_SLB_3.root ${data_folder}/run_${run}*/*dat_SLB_3.root
	sleep 20
    fi
fi

root -l CommissioningAnalysis.cc\(\"../../SLB_data/run_${run}\",\"_run_${run}\",\"_SLB_0\"\) &
root -l CommissioningAnalysis.cc\(\"../../SLB_data/run_${run}\",\"_run_${run}\",\"_SLB_1\"\) 

root -l CommissioningAnalysis.cc\(\"../../SLB_data/run_${run}\",\"_run_${run}\",\"_SLB_2\"\) &
root -l CommissioningAnalysis.cc\(\"../../SLB_data/run_${run}\",\"_run_${run}\",\"_SLB_3\"\)

