#!/bin/bash
if [ "$1" == "" ];then 
	echo "please input performance file name"
	exit 1
fi
if [ ! -f $1 ];then 
	echo "file $1 does not exist"
	exit 1
fi 
if [ "$2" == "" ];then 
	echo "please input disk name, e.g., dm-0"
	exit 1
fi
grep $2 $1 |tail -n 20|tr -s [:space:]|cut -d" " -f2|awk '{ print $1/1024}'|awk '{sum += $1} END {print sum/20}' 
