#!/bin/bash

#Note: before replay, we need first create cache devices that
#users will use, e.g., cachedev0 ,cachedev1,...,cachedev15.
#We can create a device for one channel or multiple channels.
#We also need to create a file name replay_all.conf, and write
#user configurations in it with this format:
#user_id, channel_id, cache_offset(GB), cache_size(GB), origin device path, trace file name

if [ ! -f "replay_all.conf" ];then
  echo "ERROR:please edit the repla_all.conf file!"
  exit 1
fi
if [ "$1" == "-i" ];then 
	for dm in $(cat replay_all.conf)
	do 
		#format in replay_all.conf
		#user_id,ch_id,off(GB),size(GB),odev,trace
		user_id=$(echo $dm |cut -d"," -f1)  #user id for dm-cache, unique for each user
		ch_id=$(echo $dm |cut -d"," -f2)    #user channel id
		off=$(echo $dm |cut -d"," -f3)      #user cache offset in this channel(GB)
		size=$(echo $dm |cut -d"," -f4)     #user cache size in this channel(GB)
		odev=$(echo $dm |cut -d"," -f5)     #user origin ddevice, unique for each user
		trace=$(echo $dm |cut -d"," -f6)    #user trace file

		#create this user
		./dm_one_user.sh -i $user_id $ch_id $off $size $odev
		if [ $? != 0 ];then
			exit 1
		fi
		echo "create user $user_id ... done!"
		#replay trace file for user 
		nohup ./replay -a 4K -b 4K -n 128 -s 900G -t 1600 /dev/mapper/my_cache$user_id $trace >"$user_id"_replay.perf&
	done
	nohup collectl -sDcm -i 10 -c 160 >4_users_replay.perf& 
elif [ "$1" == "-f" ];then 
	for dm in $(cat replay_all.conf)
	do 
		user_id=$(echo $dm |cut -d"," -f1)  #user id for dm-cache, unique for each user
		./dm_one_user.sh -f $user_id
		if [ $? != 0 ];then
			exit 1
		fi
		echo "destroy dm-cache $user_id ... done!"
	done
else
	echo "usage: ./replay_all.sh -i to replay all users"
	echo "       ./replay_all.sh -f to destroy all users"
fi
