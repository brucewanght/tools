#!/bin/bash

if [ "$1" == "" ];then
	echo "please input dm-cache user id"
	exit 1
fi

#check if dm-cache target exist
live=$(ls /dev/mapper/ |grep my_cache$1)
if [ "$live" != "" ];then
    echo "test device my_cache$1"
else 
	echo "my_cache$1 doesn't exist!"
	exit 1
fi

if [ "$2" == "" ];then 
	tm=120
	echo "default run time is $tm seconds"
else
	tm=$2
	echo "set run time to $tm seconds"
fi

iomode=(write read randwrite randread)
dev="/dev/mapper/my_cache$1"
echo "test device $1"
for mode in ${iomode[@]}
do
    echo "test $mode"
    for i in $(seq 5)
    do
    	fio -filename=$dev -direct=1 -iodepth 128 -thread -rw=$mode  -ioengine=libaio -bs=4K -numjobs=1 -runtime=$tm -group_reporting -name=dm-cache$1-$mode >>fio-$1-$mode
    done
done
