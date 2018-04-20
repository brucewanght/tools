#!/bin/bash

cache="/dev/mapper/my_cache1"
if [ -e $cache ]; then
	echo > 1id_rwcheck.log
else
	echo "ERROR: $cache dose not exist!"
	exit 1
fi

for i in $(seq 0 4096)
do
	dd if=data1 of=write1 bs=32K skip=$i count=1 2>>/dev/null
	dd if=data1 of=$cache bs=32K skip=$i seek=$i count=1 2>>/dev/null 
	dd if=$cache of=read1 bs=32K skip=$i count=1 2>>/dev/null
	same=$(diff write1 read1)
	if ["$same" = ""];then
		echo "cache block $i is intact.">>1id_rwcheck.log
	else 
		echo "ERROR: cache block $i is corrupted!">>1id_rwcheck.log
	fi
done
