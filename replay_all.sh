#!/bin/bash

#Note: before replay, we need first create cache devices that
#users will use, e.g., cachedev0 ,cachedev1,...,cachedev15.
#We can create a device for one channel or multiple channels.
#We also need to create a config file, and write user configurations 
#in it with this format:
#uid, channel_id, cache_offset(GB), cache_size(GB), origin device path, trace file name

if [ "$1" == "-r1" ];then 
    if [ ! -f "dm_isolation.conf" ];then
      echo "ERROR:please edit the dm_isolation.conf file!"
      exit 1
    fi
	echo "replay for channel isolation dm-cache users ..."
	for dm in $(cat dm_isolation.conf)
	do 
		#format in replay_all.conf
		#uid,cid,off(GB),size(GB),odev,trace_file
		uid=$(echo $dm |cut -d"," -f1)  #user id for dm-cache, unique for each user
		cid=$(echo $dm |cut -d"," -f2)    #user channel id
		off=$(echo $dm |cut -d"," -f3)      #user cache offset in this channel(GB)
		size=$(echo $dm |cut -d"," -f4)     #user cache size in this channel(GB)
		odev=$(echo $dm |cut -d"," -f5)     #user origin ddevice, unique for each user
		trace_file=$(echo $dm |cut -d"," -f6)
		delay_us=$(echo $dm |cut -d"," -f7)
		burst_s=$(echo $dm |cut -d"," -f8)

		#create this user
		./dm_one_user.sh -i $uid $cid $off $size $odev
		if [ $? != 0 ];then
			exit 1
		fi
		echo "create user $uid ... done!"
		#replay trace_file file for user 
		nohup ./replay -a 4K -b 4K -n 128 -s 900G -t 1000 -D $delay_us -I $burst_s /dev/mapper/my_cache$uid $trace_file&
	done
	nohup collectl -sDcm -i 5 -c 200 >4_users_replay.perf& 
elif [ "$1" == "-r2" ];then 
    if [ ! -f "dm_hotcold.conf" ];then
      echo "ERROR:please edit the dm_hotcold.conf file!"
      exit 1
    fi
	echo "replay for hot/cold channel isolation dm-cache users ..."
	for dm in $(cat dm_hotcold.conf)
	do 
		#format in replay_all.conf
		#uid,hid,cid,hoff(GB),hsize(GB),coff,csize,odev,trace_file
		uid=$(echo $dm |cut -d"," -f1)  #user id for dm-cache, unique for each user
		hid=$(echo $dm |cut -d"," -f2)  #user hot channel id
		cid=$(echo $dm |cut -d"," -f3)  #user cold channel id
		hoff=$(echo $dm |cut -d"," -f4) #user cache offset in hot channel(GB)
		hsize=$(echo $dm |cut -d"," -f5) #user cache size in hot channel(GB)
		coff=$(echo $dm |cut -d"," -f6) #user cache offset in cold channel(GB)
		csize=$(echo $dm |cut -d"," -f7) #user cache size in cold channel(GB)
		odev=$(echo $dm |cut -d"," -f8) #user origin ddevice, unique for each user
		trace_file=$(echo $dm |cut -d"," -f9)
		delay_us=$(echo $dm |cut -d"," -f10)
		burst_s=$(echo $dm |cut -d"," -f11)

		#create this user
		./dm_one_user_hotcold.sh -i $uid $hid $cid $hoff $hsize $coff $csize $odev
		if [ $? != 0 ];then
			exit 1
		fi
		echo "create user $uid ... done!"
		#replay trace_file file for user 
		#nohup ./replay -a 4K -b 4K -n 128 -s 900G -t 800 -D 5000 /dev/mapper/my_cache$uid $trace_file >"$uid"_replay.perf&
		nohup ./replay -a 4K -b 4K -n 128 -s 900G -t 1000 -D $delay_us -I $burst_s /dev/mapper/my_cache$uid $trace_file&
	done
	nohup collectl -sDcm -i 10 -c 160 >4_users_hotcold.perf& 
elif [ "$1" == "-f1" ];then 
	for dm in $(cat dm_isolation.conf)
	do 
		uid=$(echo $dm |cut -d"," -f1)  #user id for dm-cache, unique for each user
		./dm_one_user.sh -f $uid
		if [ $? != 0 ];then
			exit 1
		fi
		echo "destroy dm-cache $uid ... done!"
	done
elif [ "$1" == "-f2" ];then 
	for dm in $(cat dm_hotcold.conf)
	do 
		uid=$(echo $dm |cut -d"," -f1)  #user id for dm-cache, unique for each user
		./dm_one_user_hotcold.sh -f $uid
		if [ $? != 0 ];then
			exit 1
		fi
		echo "destroy dm-cache $uid ... done!"
	done
else
	echo "usage: ./replay_all.sh -r1 to replay all users for channel isolation"
	echo "       ./replay_all.sh -r2 to replay all users for hot/cold cache isolation"
	echo "       ./replay_all.sh -f1 to destroy all users created bt r1"
	echo "       ./replay_all.sh -f2 to destroy all users created bt r2"
fi
