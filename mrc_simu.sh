#!/bin/bash
if [ "$1" == "" ];then
	echo "please input cache policy: lru or smq"
	exit 1
elif [ "$1" == "lru" ];then 
	policy="lru"
	echo "cache policy: $policy"
elif [ "$1" == "smq" ];then 
	policy="smq"
	echo "cache policy: $policy"
else
	echo "wrong policy: $policy"
	exit 1
fi

if [ "$2" == "" ];then 
	echo "please input trace path!"
	exit 1
elif [ ! -f $2 ];then 
	echo "trace $2 doesn't exist!"
	exit 1
else 
	trace=$2
	echo "trace file: $trace"
fi

if [ "$3" == "" ];then 
	echo "please input cache size(GB)"
	exit 1
fi
mb_size=$(awk 'BEGIN{print '$3'*1024}')

if [ "$4" == "" ];then 
	echo "please input IO block size(KB)"
	exit 1
fi
io_size="$4K"

#check if dm-cache target exist, and remove it
live=$(ls /dev/mapper/ |grep my_cache0) 
if [ "$live" != "" ];then
	echo "remove old my_cache0"
	./dm_one_user.sh -f 0
	losetup -d /dev/loop0 
	losetup -d /dev/loop1 
	if [ $? != 0 ];then
		exit 1
	fi
fi 
dd if=/dev/zero of=/tmp/meta0.img bs=1M count=4096 >/dev/null 2>&1
dd if=/dev/zero of=/tmp/cache.img bs=1M count=$mb_size >/dev/null 2>&1
echo "set up loop devices"
losetup /dev/loop0 /tmp/meta0.img 
losetup /dev/loop1 /tmp/cache.img 
orig_size=$(blockdev --getsz /dev/sdd)
cache_size=$(blockdev --getsz /dev/loop1)
echo "set up dm-cache"
dmsetup create my_cache0 --table '0 '$orig_size' cache 0 1 /dev/loop0 /dev/loop /dev/nvme0n1 64 0 '$cache_size' 1 writeback '$policy' 0'

if [ $? != 0 ];then
	echo "set up dm-cache failed, detach loop devices"
	losetup -d /dev/loop0
	losetup -d /dev/loop1
	exit 1
fi

echo "replay trace"
./replay -a $io_size -b $io_size -n 128 -s 900G /dev/mapper/my_cache0 $trace
echo "$trace, $policy, 10G" >>mrc_simu.log
echo "caculate miss ratio"
./miss_ratio.sh 0 mrc_simu.log
sleep 20
echo "destroy dm-cache"
dmsetup remove /dev/mapper/my_cache0
losetup -d /dev/loop0
losetup -d /dev/loop1
echo "done!"
