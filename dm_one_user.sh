#!/bin/bash

if [ "$1" = "-i" ];then 
	if [ "$2" = "" ];then 
		echo "please input user id"
		exit 1
	fi

	if [ "$3" = "" ];then 
		echo "please input channel id"
		exit 1
	fi

	if [ "$4" = "" ];then 
		echo "please input cache dev offset(GB)"
		exit 1
	fi

	if [ "$5" = "" ];then 
		echo "please input cache size(GB)"
		exit 1
	fi
	
	if [ "$6" = "" ];then 
		echo "please input origin device"
		exit 1
	fi

	#if [ "$7" = "" ];then 
	#	echo "please input cache device base name, e.g., cachedev"
	#	exit 1
	#fi

	echo "set meta device"

	dd if=/dev/zero of=/tmp/meta$2.img bs=1M count=2048
	losetup /dev/loop$2 /tmp/meta$2.img 

	#cache block size is 32K
    sectors=$(blockdev --getsz /dev/sdd)	
    offs=$(awk 'BEGIN{print '$4'*1024*1024/32}')
    cbks=$(awk 'BEGIN{print '$5'*1024*1024/32}')

	echo "set up dm-cache device"
	dmsetup create my_cache$2 --table '0 '$sectors' cache '$2' '$3' '/dev/loop$2' /dev/cachedev '$6' 64 '$offs' '$cbks' 1 writeback default 0'
	if [ $? != 0 ];then
		echo "set up dm-cache failed!"
		losetup -d /dev/loop$2
		exit 1
	fi
	echo "done"
elif [ "$1" = "-f" ];then 
	if [ "$2" = "" ];then 
		echo "please input user id"
		exit 1
	fi
	echo "remove dm-cache target"
	dmsetup remove /dev/mapper/my_cache$2

	echo "detach meta devices"
	losetup -d /dev/loop$2

	echo "remove meta data"
	rm /tmp/meta$2.img

	echo "done"
else
  echo "wrong parameter!"
  echo "Usage:"
  echo "init dm-cache: ./dm_one_user.sh -i user_id channel_id cache_size(GB) orig_dev"
  echo "free dm-cache: ./dm_one_user.sh -f id"
  exit 1
fi
