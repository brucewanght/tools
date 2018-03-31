#!/bin/bash

if [ ! -f dm_replay.conf ];then 
	echo "please set the dm_replay.conf file"
	echo "format: dm-cache id:trace, e.g.:"
	echo "0:w001"
	echo "1:w003"
	exit 
fi
for p in $(cat dm_replay.conf)
do
	id=$(echo $p |cut -d":" -f1)
	trace=$(echo $p |cut -d":" -f2)

done
if [ "$1" == "" ];then 
	echo "please input dm-cache id, e.g., 0,1..."
	exit 1
fi
if [ "$2" == "" ];then 
	echo "please input trace file name"
	exit 1
fi
if [ "$3" == "" ];then 
	echo "please input log file name"
	exit 1
fi
nohup collectl -sDcm -i 10 -c 60 >"$3"&
./replay -a 4K -b 4K -n 128 -s 900G -t 600 /dev/mapper/my_cache$1 $2
grep dm-$1 $3|tr -s [:space:]|cut -d" " -f2|awk '{ print $1/1024}'
