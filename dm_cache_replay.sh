#!/bin/bash

if [ "$1" == "" ];then 
	echo "please input trace name!"
	exit 1
fi
if [ ! -f $1 ];then 
	echo "trace file $1 dosen't exist!"
	exit 1
fi
trace_file=$1
trace=$(echo $1|cut -d"/" -f2)
echo "trace file: $trace"

ch=$2
if [ "$ch" == "" ];then 
	echo "default channel number is 16"
	ch=16
elif [ "$ch" -gt 16 ];then
	echo "invalid channel number: $ch, must be in [1, 16]"
elif [ "$ch" -lt 1 ];then
	echo "invalid channel number: $ch, must be in [1, 16]"
else 
	echo "channel number is $ch"
fi

policy=$3;
if [ "$policy" == "" ];then 
	echo "please input cache policy: lru or smq"
	exit 1
elif [ "$policy" != "lru" -a "$policy" != "smq" ];then
	echo "policy must be lru or smq!"
	exit 1
fi

tm=$4
if [ "$tm" == "" ];then 
	echo "default run time is 600 seconds"
	tm=600
else
	echo "run time is $tm seconds"
fi

#check if dm-cache target exist, and remove it
live=$(ls /dev/mapper/ |grep my_cache0) 
if [ "$live" != "" ];then
	echo "remove old my_cache0"
	./dm_one_user.sh -f 0
	if [ $? != 0 ];then
		exit 1
	fi
fi

##check if pblk cachedev0 exist
#dev_live=$(ls /dev/ |grep cachedev0) 
#if [ "$dev_live" != "" ];then
#	echo "remove old cachedev0"
#    nvme lnvm remove nvme2n1 -n cachedev0 
#fi
#
##create cachedev0 according channel number
#begch=$(awk 'BEGIN{print '$ch'*8}')
#endch=127
#nvme lnvm create -d nvme2n1 -n cachedev0 -t pblk -b $begch -e $endch -f
#if [ $? != 0 ];then 
#	exit 1
#fi

sectors=$(blockdev --getsz /dev/sdd)
size=(1 2 4 10 50 100 200 400 800)
#mrcf="$trace"_"$policy"_"$ch".mrc
#perf="$trace"_"$policy"_"$ch".perf
mrcf="$trace"_"$policy".mrc
#echo "mrc file $mrcf, perf file $perf"

#collect interval is 10s, and count is time/interval
int=10
cnt=$(awk 'BEGIN{print '$tm'/'$int'}')

for size in ${size[@]}
do
	echo "test cache size: $size"
	./dm_one_user.sh -i 0 1 0 $size /dev/sdd /dev/nvme0n
	#nohup collectl -sDcm -i $int -c $cnt >"$perf"_"$size"& 
	#-w means writing data 
	#./replay -a 4K -b 4K -n 128 -s 900G -t $tm /dev/mapper/my_cache0 $trace_file >>$perf 
	./replay -a 4K -b 4K -n 128 -s 900G -t $tm /dev/mapper/my_cache0 $trace_file
	sleep 10
	./miss_ratio.sh 0 $mrcf
	./dm_one_user.sh -f 0
done
