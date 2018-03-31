#!/bin/bash
if [ "$1" == "" ];then 
	echo "please input performance file name"
	exit 1
fi
perf=$1
out=sum_"$perf"
>$out 
for i in $(seq 1 1000)
do
    perf_file="$perf".perf_"$i"
	if [ ! -f $perf_file ];then 
		continue
	fi
	grep dm $perf_file |tail -n 20|tr -s [:space:]|cut -d" " -f2|awk '{ print $1/1024}'|awk '{sum += $1} END {print sum/20}'>>$out 
done
