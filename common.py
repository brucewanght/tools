#!/usr/bin/python3
import fileinput
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.rcParams['hatch.linewidth'] = 0.5

# extract content
def value_at(tokens, key, offset):
  r = range(0, len(tokens))
  for i in r:
    if tokens[i] == key:
      vi = i + offset
      if vi in r:
        return tokens[vi]
      else:
        break
  return None

#returns the text contents at certain position
def parse_perf_xy_all(fn, filters, xp, yp):
  xy=[]
  with fileinput.input(files=fn) as fi:
    for line in fi:
      tokens = line.split(' ')
      keep = True
      for (key, off, txt) in filters:
        val = value_at(tokens, key, off)
        if val != txt:
          keep = False
          break
      if keep is True:
        x = value_at(tokens, xp[0], xp[1])
        y = value_at(tokens, yp[0], yp[1])
        if x is not None and y is not None:
          xy.append((x,y))
  return xy

def parse_perf_num(fn, filters, xp):
  xs=[]
  with fileinput.input(files=fn) as fi:
    for line in fi:
      tokens = line.split(' ')
      keep = True
      for (key, off, txt) in filters:
        val = value_at(tokens, key, off)
        if val != txt:
          keep = False
          break
      if keep is True:
        x = value_at(tokens, xp[0], xp[1])
        if x is not None:
          xs.append(float(x))
  return xs

# sort by x, remove redundent xs
def max_sort_float(xys):
  m = {}
  for (x,y) in xys:
    xx = float(x)
    yy = float(y)
    if xx in m:
      if m[xx] < yy:
        m[xx] = yy
    else:
      m[xx] = yy
  s0 = [(x,m[x]) for x in m.keys()]
  s1 = sorted(s0, key=lambda e : e[0])
  return s1

#              red       orange     green       blue        pink     brown      purple
defcolors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#e377c2', '#8c564b', '#9467bd']
defhatchs = ['---', 'xxx', '///', '\\\\\\', '...', 'ooo']
# tag: output filename
# [sys][idx]xs: 2darray, each array is the value of a system in systems
# []sysnames: names of the systems (Label)
# []binlabels: name of each group of tests (x axis)
# []colors: color for each system
def plot_bars(tag, xs, sysnames, binnames, **kwargs):
  nr_sys = len(sysnames)
  nr_bin = len(binnames)
  fig,ax = plt.subplots(1, 1, figsize=kwargs.get("plotsize", (4.8,3.0)))
  ymax = 0.0
  colors = kwargs.get('colors', defcolors)
  hatchs = kwargs.get('hatchs', defhatchs)
  for (i, x, sys, color, hatch) in list(zip(list(range(0, nr_sys)), xs, sysnames, colors, hatchs)):
    xpos = [x + i for x in range(0, (nr_bin) * (nr_sys + 1), nr_sys + 1)]
    xmax = max(x)
    if xmax > ymax:
      ymax = xmax
    ax.bar(xpos, x, 1, align='edge', hatch=hatch, edgecolor='k', lw=0.5, facecolor=color, label=sys)
  ymax = kwargs.get("ymax", ymax * 1.2)
  ax.set_ylim(0, ymax)
  ax.grid(True, axis='y', linestyle='--', lw=0.5, color='#666666')
  ax.set_xlabel(kwargs.get("xlabel", ""), size=kwargs.get("xlabelsize", 12))
  ax.set_ylabel(kwargs.get("ylabel", ""), size=kwargs.get("xlabelsize", 12))
  ncol=kwargs.get("ncol", 4)
  ax.legend(loc=kwargs.get("loc", "upper center"), ncol=ncol, borderpad=0.2, framealpha=1, labelspacing=0.0)
  xticks = [x + (nr_sys/2) for x in range(0, (nr_bin) * (nr_sys + 1), nr_sys + 1)]
  ax.set_xticks(xticks)
  ax.set_xticklabels(binnames)
  fig.savefig('%s.pdf' % tag, bbox_inches='tight', pad_inches=0, format='pdf')
  plt.close(fig)

def extract_values(epoch, sysorders, sizes, traces, machines, fltr, xp, selectf):
  xs = {}
  for sys in sysorders:
    ss = []
    print(sys)
    for (size, trace) in list(zip(sizes, traces)):
      vs = []
      for m in machines:
        fn = "%s/%s-%s-%d-%s.txt" % (m, epoch, sys, size, trace)
        v = parse_perf_num(fn, fltr, xp)
        vs.append(selectf(v))
      vs.sort()
      vs = vs[1:-1]
      print(vs)
      ss.append(statistics.mean(vs))
    xs[sys] = ss

  dataset = [xs[sname] for sname in sysorders]
  return dataset

def normalize_dataset(dataset, nr_sys, nr_bin):
  # post processing
  for i in range(0, nr_bin):
    bins=[]
    for s in range(0, nr_sys):
      bins.append(dataset[s][i])
    bmax=max(bins)
    for s in range(0, nr_sys):
      dataset[s][i] = dataset[s][i] / bmax
