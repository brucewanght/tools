#!/bin/bash

if [ "$1" == "-i" ];then 
	if [ "$2" == "" ];then 
		echo "please input lightnvm device, e.g., nvme1n1"
		exit 1
	fi
	dev_live=$(ls /dev/ |grep cachedev)
	if [ "$dev_live" == "" ];then
		echo "create cachedev with pblk"
		for i in $(seq 0 15)
		do
            begin=$(awk 'BEGIN{print '$i'*8}')
			end=$(awk 'BEGIN{print '$begin'+7}')
			nvme lnvm create -d $2 -n cachedev$i -t pblk -b $begin -e $end -f
			if [ $? != 0 ];then
				exit 1
			fi
			echo "create cachedev$i ... OK"
	    done
	else 
		echo "already has cachedev"
	fi 
elif [ "$1" == "-f" ];then 
	if [ "$2" == "" ];then 
		echo "please input lightnvm device, e.g., nvme1n1"
		exit 1
	fi
	dev_live=$(ls /dev/ |grep cachedev)
	if [ "$dev_live" != "" ];then
		echo "remove pblk dev"
		for i in $(seq 0 15)
		do
			nvme lnvm remove $2 -n cachedev$i
			if [ $? != 0 ];then
				exit 1
			fi
			echo "remove cachedev$i ... OK"
	    done
	else 
		echo "no cachedev"
	fi 
else 
	echo "wrong arguments: "
	echo "careate device: ./set_up_pblk.sh -i nvme1n1"
	echo "destroy device: ./set_up_pblk.sh -f nvme1n1"
fi
