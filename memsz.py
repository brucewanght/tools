#!/usr/bin/python3
import sys
import math
import numpy

exec(open('common.py').read())

sysorders = ["skiplist", "bptree", "masstree", "wormhole", "array"]
sysnames = ["Skip List", "B+-tree", "Masstree", "Wormhole", "Array"]
colors_all = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#8c564b', '#e377c2', '#9467bd']
binnames = ["Az1", "Az2", "Meme", "k3", "k4", "k6", "k8", "k10"]
sls = [13185, 13184, 26425, 31026, 23193, 14700, 12247, 10386]
bts = [13519, 12159, 26921, 31726, 23630, 15277, 12565, 10565]
mts = [17995, 25805, 38200, 26152, 27125, 25631, 27870, 26268]
whs = [12927, 13678, 27651, 25716, 21538, 14190, 12059, 10335]
arr = [8693, 8693, 19606, 19073, 11444, 10070, 10681, 9995]
alls = [sls, bts, mts, whs, arr]
for i in range(0, len(sysorders)):
  alls[i] = [x / 1024.0 for x in alls[i]]

# low throughputs on u10
sizes = [142411471, 142411471, 192678503, 500000000, 300000000, 120000000, 40000000, 10000000]

plot_bars("50-size", alls, sysnames, binnames, ylabel="Memory Usage (GB)", ncol=1, loc="upper left", colors=colors_all, ymax=41.0)
