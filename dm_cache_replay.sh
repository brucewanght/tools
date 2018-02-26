#!/bin/bash

if [ "$1" == "" ];then 
	echo "please input trace name!"
	exit 1
fi

policy=$2;
if [ "$policy" == "" ];then 
	echo "please input cache policy: lru or smq"
	exit 1
elif [ "$policy" != "lru" -a "$policy" != "smq" ];then
	echo "policy must be lru or smq!"
	exit 1
fi

tm=$3
if [ "$tm" == "" ];then 
	echo "default run time is 300 seconds"
	tm="300"
else
	echo "run time is $tm seconds"
fi

if [ ! -f $1 ];then 
	echo "trace file $1 dosen't exist!"
	exit 1
fi

#cache block size is 32K

live=$(ls /dev/mapper/ |grep my_cache) 
if [ "$live" != "" ];then
	echo "remove old my_cache"
	dmsetup remove /dev/mapper/my_cache 
	losetup -d /dev/loop6 
	if [ $? != 0 ];then
		exit 1
	fi
fi

dev_live=$(ls /dev/ |grep cachedev0) 
if [ "$dev_live" == "" ];then
	echo "cachedev0 doesn't exist!"
	exit 1
fi

sectors=$(blockdev --getsz /dev/sdd)
size=(1 2 3 4 5 6)
mrcf="my_cache_$policy.mrc"
perf="my_cache_$policy.perf"
for size in ${size[@]}
do
	cbks=$(awk 'BEGIN{print '$size'*1024*1024/32}')
	echo "test cache size: $size, cache blocks: $cbks"

	dd if=/dev/zero of=/tmp/meta.img bs=1M count=2048
	losetup /dev/loop6 /tmp/meta.img
	if [ $? != 0 ];then
		exit 1
	fi

	dmsetup create my_cache --table '0 '$sectors' cache 0 0 /dev/loop6 /dev/cachedev /dev/sdd 64 0 '$cbks' 1 writeback '$policy' 0'

	if [ $? != 0 ];then
		echo "create dm-cache failed!"
		exit 1
	fi

	./replay -a 4K -b 4K -n 32 -s 900G -t $tm /dev/mapper/my_cache $1 >>$perf 
	./miss_ratio.sh $mrcf 

	dmsetup remove /dev/mapper/my_cache 
	losetup -d /dev/loop6 
done
