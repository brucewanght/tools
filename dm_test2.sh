#!/bin/bash

cache1="/dev/mapper/my_cache1"
cache2="/dev/mapper/my_cache2"
if [ -e $cache1 ]; then
	if [ -e $cache2 ];then 
		echo > 2id_rwcheck.log 
	else 
		echo "ERROR $cache2 dose not exist!"
	    exit 1
	fi 
else
	echo "ERROR: $cache1 dose not exist!"
	exit 1
fi

for i in $(seq 0 65535)
do
	dd if=data1 of=write1 bs=32K skip=$i count=1 2>>/dev/null
	dd if=data2 of=write2 bs=32K skip=$i count=1 2>>/dev/null 

	dd if=data1 of=$cache1 bs=32K skip=$i seek=$i count=1 2>>/dev/null
	dd if=data2 of=$cache2 bs=32K skip=$i seek=$i count=1 2>>/dev/null
	dd if=$cache1 of=read1 bs=32K skip=$i count=1 2>>/dev/null 

	dd if=data1 of=$cache1 bs=32K skip=$i seek=$i count=1 2>>/dev/null
	dd if=$cache2 of=read2 bs=32K skip=$i count=1 2>>/dev/null 

	#check if data is correct
	same1=$(diff write1 read1)
	same2=$(diff write2 read2)

	if [ "$same1" = "" ];then
		echo "cache1 block $i is intact." >>2id_rwcheck.log
	else 
		echo "ERROR: cache1 block $i is corrupted!" >>2id_rwcheck.log 
	fi

	if [ "$same2" = "" ];then
		echo "cache2 block $i is intact." >>2id_rwcheck.log
	else 
		echo "ERROR: cache2 block $i is corrupted!" >>2id_rwcheck.log 
	fi
done
