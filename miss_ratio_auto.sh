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
	echo "default collect interval is 10 seconds"
	int=10
else
	int=$3
	echo "collect interval is $3 seconds"
fi 

if [ "$4" == "" ];then 
	echo "default collect count is 60"
	count=60
else 
	count=$4
	echo "collect count is $4"
fi

#collect fixed number of miss ratios 
for i in $(seq 1 $count)
do
	read_hits=$(dmsetup status my_cache$1|cut -d" " -f8)
	read_misses=$(dmsetup status my_cache$1|cut -d" " -f9)
	write_hits=$(dmsetup status my_cache$1|cut -d" " -f10)
	write_misses=$(dmsetup status my_cache$1|cut -d" " -f11)
	hits=$(awk 'BEGIN{print '$read_hits'+'$write_hits'}')
	misses=$(awk 'BEGIN{print '$read_misses'+'$write_misses'}')
	cbk_size=$(dmsetup status my_cache$1|cut -d" " -f6)
	cbks=$(dmsetup status my_cache$1|cut -d" " -f7|cut -d"/" -f2)
	#cache_size in GB
	cache_size=$(awk 'BEGIN{print '$cbks'*'$cbk_size'/2048/1024}')
	miss_ratio=$(awk 'BEGIN{print '$misses'/('$misses' + '$hits')}')
	echo "$cache_size, $misses, $hits, $miss_ratio"
	echo "$cache_size, $misses, $hits, $miss_ratio" >>$2
	sleep $int 
done
