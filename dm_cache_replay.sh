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

if [ ! -f $1 ];then 
	echo "trace file $1 dosen't exist!"
	exit 1
fi

#cache block size is 32K

live=$(ls /dev/mapper/ |grep my_cache1) 
if [ "$live" != "" ];then
	echo "remove old my_cache1"
	dmsetup remove /dev/mapper/my_cache1 
	losetup -d /dev/loop6 
	if [ $? != 0 ];then
		exit 1
	fi
fi

dev_live=$(ls /dev/ |grep cachedev) 
if [ "$dev_live" == "" ];then
	echo "create cachedev with pblk"
	nvme lnvm create -d nvme1n1 -n cachedev -t pblk -b 0 -e 127 -f
	if [ $? != 0 ];then
		exit 1
	fi
fi

for size in $(seq 90 100)
do
	cbks=$(awk 'BEGIN{print '$size'*1024*1024/32}')
	echo "test cache size: $size, cache blocks: $cbks"

	dd if=/dev/zero of=/tmp/meta.img bs=1M count=1024
	losetup /dev/loop6 /tmp/meta.img
	if [ $? != 0 ];then
		exit 1
	fi

	dmsetup create my_cache1 --table '0 625142448 cache 0 1 /dev/loop6 /dev/cachedev /dev/sdc 64 '$cbks' 1 writeback '$policy' 0'
	if [ $? != 0 ];then
		exit 1
	fi

	for i in $(seq 1 5)
	do
		./replay -a 4K -b 4K -n 32 -s 900G /dev/mapper/my_cache1 $1 >>$1_$policy.perf
	done

	if [ $? != 0 ];then
		exit 1
	fi
	./miss_ratio.sh my_cache1_$1_$policy.mrc

	dmsetup remove /dev/mapper/my_cache1 
	losetup -d /dev/loop6 
done
