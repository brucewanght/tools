#!/bin/bash
chb=$1
che=$2
lunb=$3
lune=$4
for i in $(seq 0 1064)
do
   nvm_vblk line_erase /dev/nvme1n1 $chb $che $lunb $lune $i >>erase.log
done
