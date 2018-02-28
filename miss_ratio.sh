#!/bin/bash
if [ "$1" == "" ];then 
	echo "please input dm-cache user id"
	exit 1
fi

if [ "$2" == "" ];then 
	echo "please input mrc log file name"
	exit 1
fi 

if [ "$3" == "" ];then 
	echo "default collect interval is 2 seconds"
	int=2
else
	int=$3
fi 
while true;do
sleep $int 
	hits=$(dmsetup status my_cache$1|cut -d" " -f8)
	misses=$(dmsetup status my_cache$1|cut -d" " -f9)
	cbk_size=$(dmsetup status my_cache$1|cut -d" " -f6)
	cbks=$(dmsetup status my_cache$1|cut -d" " -f7|cut -d"/" -f2)
	#cache_size in GB
	cache_size=$(awk 'BEGIN{print '$cbks'*'$cbk_size'/2048/1024}')
	miss_ratio=$(awk 'BEGIN{print '$misses'/('$misses' + '$hits')}')
	echo "$cache_size, $misses, $hits, $miss_ratio"
	echo "$cache_size, $misses, $hits, $miss_ratio" >>$2
done
