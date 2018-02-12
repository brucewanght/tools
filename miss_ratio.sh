#!/bin/bash

hits=$(dmsetup status my_cache1|cut -d" " -f8)
misses=$(dmsetup status my_cache1|cut -d" " -f9)
cbk_size=$(dmsetup status my_cache1|cut -d" " -f6)
cbks=$(dmsetup status my_cache1|cut -d" " -f7|cut -d"/" -f2)
echo "hits=$hits, misses=$misses, cbk_size=$cbk_size, cbks=$cbks"
#cache_size in GB
cache_size=$(awk 'BEGIN{print '$cbks'*'$cbk_size'/2048/1024}')
miss_ratio=$(awk 'BEGIN{print '$misses'/('$misses' + '$hits')}')

echo "$cache_size, $misses, $hits, $miss_ratio" >>$1
