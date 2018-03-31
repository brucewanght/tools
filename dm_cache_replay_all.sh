#!/bin/bash

if [ "$1" == "" ];then 
	echo "please input trace name!"
	exit 1
fi

if [ ! -f $1 ];then 
	echo "trace file $1 dosen't exist!"
	exit 1
fi

channel=(8)

for ch in ${channel[@]}
do
	echo "number of channels: $ch"
    ./dm_cache_replay.sh $1 $ch smq 600
done
