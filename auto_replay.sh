#!/bin/bash

#Note: before replay, we need first create cache devices that
#users will use, e.g., cachedev0 ,cachedev1,...,cachedev15.
#We can create a device for one channel or multiple channels.
#We also need to create a config file, and write user configurations 
#in it with this format:
#uid, channel_id, cache_offset(GB), cache_size(GB), origin device path, trace file name

if [ "$1" == "-s" ];then 
	conf="0-shared-cache.conf"
	perf="0-shared-cache.perf"
elif [ "$1" == "-i" ];then 
    conf="1-iso-cache.conf"
	perf="1-iso-cache.perf"
elif [ "$1" == "-o" ];then 
	conf="2-oc-cache.conf"
	perf="2-oc-cache.perf"
elif [ "$1" == "-fs" ];then 
	conf="0-shared-cache.conf"
	free=1
elif [ "$1" == "-fi" ];then 
    conf="1-iso-cache.conf"
	free=1
elif [ "$1" == "-fo" ];then 
	conf="2-oc-cache.conf"
	free=1
else 
	echo "ERROR: wrong parameter 1:"
	echo "-i:  iso-cache replay"
	echo "-s:  shared-cache replay"
	echo "-o:  oc-cache replay"
    exit 1
fi

if [ "$free" == 1 ];then
	for dm in $(grep ^[0-9] $conf)
	do 
		uid=$(echo $dm |cut -d"," -f1)  #user id for dm-cache, unique for each user
		./dm_one_user_hotcold.sh -f $uid
		if [ $? != 0 ];then
			exit 1
		fi
		echo "destroy dm-cache $uid ... done!"
	done
	exit 1
fi

#check if config file exists
if [ ! -f $conf ];then 
	echo "ERROR: can't find $conf!" 
	exit 1
fi

if [ "$2" != "" ];then
	perf="$perf"_"$2"
fi

#replay traces for each tenant according configure file
for dm in $(grep ^[0-9] $conf)
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
	wratio=$(echo $dm |cut -d"," -f12)

    live=$(ls /dev/mapper/ |grep my_cache$uid) 
    if [ "$live" != "" ];then
    	echo "my_cache$uid already exists!"
	else
	    #create this user
		./dm_one_user_hotcold.sh -i $uid $hid $cid $hoff $hsize $coff $csize $odev
	    if [ $? != 0 ];then
	    	exit 1
	    fi
		echo "my_cache$uid ... done!"
    fi
	#replay trace_file file for user 
	if [ "$wratio" != "0" ];then
		nohup ./replay -a 4K -b 4K -n 128 -s 900G -r 100 -t 1800 -w $wratio -D $delay_us -I $burst_s /dev/mapper/my_cache$uid $trace_file >>$conf&
	else
		nohup ./replay -a 4K -b 4K -n 128 -s 900G -r 100 -t 1800 -D $delay_us -I $burst_s /dev/mapper/my_cache$uid $trace_file >>$conf&
	fi
done
nohup collectl -sDcm -i 5 -c 360 >$perf& 

