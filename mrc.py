#coding=utf-8
"""
========
Note:
1.This script is used to read data from csv files and produce a barchar that reflect
   the comparisonof  these data.
2.Every row of csv file represent a group data 
========

A bar plot with errorbars and height labels on individual bars
"""
import csv
import os
import numpy as np
import matplotlib.pyplot as plt

'''
autoread: read data form  file to list 
'''
def autoread(filename):
    miss_ratio=[]
    cache_size=[]
    csvfile_in = open(filename, 'r')
    reader =csv.reader(csvfile_in)
    for line in reader:
        csize=int(line[5])
        mr=float(line[6])*100
        cache_size.append(csize)
        miss_ratio.append(mr)
    csvfile_in.close()
    return [cache_size,miss_ratio]

'''
plotdata: plot data to barchart
'''
def plotline(xy,name):
    fig = plt.figure(dpi=300, figsize=(10, 8))
    cache_size=xy[0]
    miss_ratio=xy[1]
    max_x=max(cache_size)
    ax = fig.add_subplot(1,1,1)
    ax.plot(cache_size, miss_ratio, 'r-',linewidth=6.0)
    
    plt.ylim(0, 100)
    plt.xlim(1,max_x)
    plt.grid()

    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    plt.xlabel('Cache Size(GB)', fontsize=22)
    plt.ylabel('Miss Ratio(%)', fontsize=22)
    #ax.set_title(name)

    #save figure as fname
    plt.savefig(name+'.pdf')  #save figure as fname
    plt.savefig(name+'.png')  #save figure as fname
    #plt.show()           #show the figure
    plt.close()

'''
main function: scan the files in current directory, find scv files and plot their data
'''
if __name__=="__main__":
    filenames=os.listdir(os.getcwd())  #get file names in current directory
    for fn in filenames:
        if fn.endswith(".mrc"):
            cache_size=[]
            miss_ratio=[]
            xy=autoread(fn)
            name=fn.split(".")[0]
            print(name)
            plotline(xy,name)
