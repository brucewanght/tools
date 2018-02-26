#!/bin/bash

if [ ! -d "$1" ]; then
  echo "directory $1 doesn't exist!"
  exit 1
fi
dir=$1

declare -a block=(4k 16k 64k 256k 1024k 4096k)
echo "sequential write" > $dir/perfdata-sw.csv
echo "block size, throughput(MB/s)" >>$dir/perfdata-sw.csv
for bk in ${block[@]}
do
	#get the throughput value, MB/s
	BW=$(grep BW $dir/fio-sw-$bk |grep -Eo 'BW=[0-9]+'|grep -Eo '[0-9]+')
	echo "$bk,$BW" >>$dir/perfdata-sw.csv
done

echo "sequential read" > $dir/perfdata-sr.csv
echo "block size, throughput(MB/s)" >>$dir/perfdata-sr.csv
for bk in ${block[@]}
do
	#get the throughput value, MB/s
	BW=$(grep BW $dir/fio-sr-$bk |grep -Eo 'BW=[0-9]+'|grep -Eo '[0-9]+')
	echo "$bk,$BW" >>$dir/perfdata-sr.csv
done

echo "random write" > $dir/perfdata-rw.csv
echo "block size, throughput(MB/s)" >>$dir/perfdata-rw.csv
for bk in ${block[@]}
do
	#get the throughput value, MB/s
	BW=$(grep BW $dir/fio-rw-$bk |grep -Eo 'BW=[0-9]+'|grep -Eo '[0-9]+')
	echo "$bk,$BW" >>$dir/perfdata-rw.csv
done

echo "random read" > $dir/perfdata-rr.csv
echo "block size, throughput(MB/s)" >>$dir/perfdata-rr.csv
for bk in ${block[@]}
do
	#get the throughput value, MB/s
	BW=$(grep BW $dir/fio-rr-$bk |grep -Eo 'BW=[0-9]+'|grep -Eo '[0-9]+')
	echo "$bk,$BW" >>$dir/perfdata-rr.csv
done

