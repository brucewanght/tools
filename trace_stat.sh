#!/bin/bash

echo "Begin stat"
echo "trace_name, lbn count, max lbn, disk_size(GB), data_size(GB), stat time elapse(s)" >trace_stat.log
for f in $(ls iomrc-u32/w*)
do
	./trace_stat $f >> trace_stat.log
done
echo "Done, results in trace_stat.log"
