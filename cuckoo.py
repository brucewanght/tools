#!/usr/bin/python3
import sys
import math
import numpy
import statistics


machines = ["u20", "u21", "u22", "u23"]
ths = [1,16]
sysorders = ["wormhole", "cuckoo2"]
sysnames = ["Wormhole", "Cuckoo"]
colors_all = ['#1f77b4', '#708090']
hatchs_all = ['\\\\\\', '**']
binnames = ["Az1", "Az2", "Meme", "k3", "k4", "k6", "k8", "k10"]
traces = [
  "azart-142411471.mmapkv", "azatr-142411471.mmapkv", "m9urls-192678503.mmapkv",
  "3a.genkv", "4a.genkv", "6a.genkv", "8a.genkv", "aa.genkv"]
sizes = [142411471, 142411471, 192678503, 500000000, 300000000, 120000000, 40000000, 10000000]

exec(open('common.py').read())

xp_all = ("mops", 1)

def plot_get_1(tag, prefix, th, ymax):
  print(tag, prefix, th, ymax)
  fltr_rp = [('rgen', 1, 'uniform'), ('pass', 1, "%d" % th)] # rand-probe
  dataset = extract_values(prefix, sysorders, sizes, traces, machines, fltr_rp, xp_all, max)
  plot_bars("%s-%s-%d" % (tag, prefix, th), dataset, sysnames, binnames, ylabel="Throughput (million ops/sec)", ymax=ymax, ncol=2, loc="upper left", colors=colors_all, hatchs=hatchs_all)

plot_get_1("36-hashget", "yh", 16, 57)
