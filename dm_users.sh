#!/bin/bash

if [ "$1" = "-i" ];then 
	echo "set up dm-cache..."
	echo "set meta devices"
	dd if=/dev/zero of=/tmp/meta0.img bs=1M count=512
	dd if=/dev/zero of=/tmp/meta1.img bs=1M count=512
	dd if=/dev/zero of=/tmp/meta2.img bs=1M count=512

	losetup /dev/loop0 /tmp/meta0.img
	losetup /dev/loop1 /tmp/meta1.img 
	losetup /dev/loop2 /tmp/meta2.img


	dev_live=$(ls /dev/ |grep cachedev)
	if [ "$dev_live" == "" ];then
		echo "create cachedev with pblk"
		for i in $(seq 0 15)
		do
            begin=$(awk 'BEGIN{print '$i'*8}')
			end=$(awk 'BEGIN{print '$begin'+7}')
			nvme lnvm create -d nvme1n1 -n cachedev$i -t pblk -b $begin -e $end -f
			if [ $? != 0 ];then
				exit 1
			fi
	    done
	else 
		echo "already has cachedev"
	fi

	
	#test: cache size is 4G, cache block size is 32K
    size=4
    cbks=$(awk 'BEGIN{print '$size'*1024*1024/32}')
    sectors0=$(blockdev --getsz /dev/sdc1)	
    sectors1=$(blockdev --getsz /dev/sdc2)	
    sectors2=$(blockdev --getsz /dev/sdc3)	

	echo "use /dev/sdc as origin devices"

	echo "set up dm-cache devices"
	dmsetup create my_cache0 --table '0 '$sectors1' cache 0 0 /dev/loop0 /dev/cachedev /dev/sdc1 64 0 '$cbks' 1 writeback smq 0'
	dmsetup create my_cache1 --table '0 '$sectors1' cache 1 0 /dev/loop1 /dev/cachedev /dev/sdc2 64 '$cbks' '$cbks' 1 writeback smq 0'
	dmsetup create my_cache2 --table '0 '$sectors2' cache 2 1 /dev/loop2 /dev/cachedev /dev/sdc3 64 0 '$cbks' 1 writeback smq 0'
	
	echo "done"
elif [ "$1" = "-f" ];then 
	echo "free dm-cache..."
	echo "remove dm-cache target"
	dmsetup remove /dev/mapper/my_cache0
	dmsetup remove /dev/mapper/my_cache1
	dmsetup remove /dev/mapper/my_cache2

	echo "detach loop devices"
	losetup -D

	echo "done"
else
  echo "wrong parameter!"
  echo "Usage:"
  echo "init dm-cache: ./dm_users.sh -i"
  echo "free dm-cache: ./dm_users.sh -f"
  exit 1
fi

