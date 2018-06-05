#!/bin/bash

if [ "$1" = "-i" ];then 
	if [ "$2" = "" ];then 
		echo "please input user id"
		exit 1
	fi

	if [ "$3" = "" ];then 
		echo "please input hot cache channel id"
		exit 1
	fi

	if [ "$4" = "" ];then 
		echo "please input cold cache channel id"
		exit 1
	fi

	if [ "$5" = "" ];then 
		echo "please input hot cache dev offset(GB)"
		exit 1
	fi

	if [ "$6" = "" ];then 
		echo "please input hot cache size(GB)"
		exit 1
	fi
	
	if [ "$7" = "" ];then 
		echo "please input cold cache dev offset(GB)"
		exit 1
	fi

	if [ "$8" = "" ];then 
		echo "please input cold cache size(GB)"
		exit 1
	fi
	
	if [ "$9" = "" ];then 
		echo "please input origin device"
		exit 1
	fi

	echo "set meta device"

	dd if=/dev/zero of=/tmp/meta$2.img bs=1M count=4096
	losetup /dev/loop$2 /tmp/meta$2.img 

	#cache block size is 32K
    sectors=$(blockdev --getsz /dev/sdd)	
    hoffs=$(awk 'BEGIN{print '$5'*1024*1024/32}')
	echo "hot off=$hoffs"
    hcbks=$(awk 'BEGIN{print '$6'*1024*1024/32}')
	echo "hot size=$hcbks"
    coffs=$(awk 'BEGIN{print '$7'*1024*1024/32}')
	echo "cold off=$coffs"
    ccbks=$(awk 'BEGIN{print '$8'*1024*1024/32}')
	echo "cold size=$ccbks"

	echo "set up dm-cache device"
	dmsetup create my_cache$2 --table '0 '$sectors' cache '$2' '$3' '$4' '/dev/loop$2' /dev/cachedev '$9' 64 '$hoffs' '$hcbks' '$coffs' '$ccbks' 1 writeback default 0'
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
	rm /tmp/meta$2.img

	echo "done"
else
  echo "wrong parameter!"
  echo "Usage:"
  echo "init dm-cache: ./dm_one_user.sh -i user_id hot_id cold_id hot_offset(GB) hot_size(GB) cold_offset(GB) cold_size(GB) orig_dev policy"
  echo "free dm-cache: ./dm_one_user.sh -f user_id"
  exit 1
fi

