#!/usr/bin/python3
import sys
import math
import numpy
import statistics


machines = ["u20", "u21", "u22", "u23"]
ths = [1,16]
sysorders = ["skiplist", "bptree", "masstree", "wormhole"]
sysnames = ["Skip List", "B+-tree", "Masstree", "Wormhole"]
colors_all = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', "#009999", "#6600cc"]
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
  plot_bars("%s-%s-abs-%d" % (tag, prefix, th), dataset, sysnames, binnames, ylabel="Throughput (million ops/sec)", ymax=ymax, ncol=1, loc="upper left")
  normalize_dataset(dataset, len(sysorders), len(binnames))
  plot_bars("%s-%s-nor-%d" % (tag, prefix, th), dataset, sysnames, binnames, ylabel="Normalized Throughput", ncol=2)

plot_get_1("30-get", "nh", 1, 2.0)
#plot_get_1("31-get", "nh", 16, 32.0)
plot_get_1("32-get", "yh", 1, 2.0)
plot_get_1("33-get", "yh", 16, 32.0)

def plot_set_1(tag, prefix, th, ymax):
  print(tag, prefix, th, ymax)
  fltr_rp = [('rgen', 1, 'counter_unsafe'), ('pass', 1, "%d" % th), ("4", 1, "100")] # rand-probe
  dataset = extract_values(prefix, sysorders, sizes, traces, machines, fltr_rp, xp_all, max)
  plot_bars("%s-%s-abs-%d" % (tag, prefix, th), dataset, sysnames, binnames, ylabel="Throughput (million ops/sec)", ymax=ymax, ncol=1, loc="upper left")

#plot_set_1("34-set", "nh", 1, 8.0)
plot_set_1("35-set", "yh", 1, 8.0)
