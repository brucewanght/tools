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
def autoread(filename,yname):
    times=[]
    perfs=[]
    csvfile_in = file(filename, 'rb')
    reader =csv.reader(csvfile_in)
    if('MB' in yname):
        for line in reader:
            time=int(line[0])/1000
            perf=float(line[1])/1000
            times.append(time)
            perfs.append(perf)
    else:
           for line in reader:
            time=int(line[0])/1000
            perf=float(line[1])/1000/1000
            times.append(time)
            perfs.append(perf)     
    csvfile_in.close()
    return times, perfs

'''
plotdata: plot data to line chart
'''
def plotline(logs, yname):
    fig = plt.figure(dpi=300,figsize=(9, 7))
    times1=[]
    perf1=[]
    times2=[]
    perf2=[]
    name1=logs[0].split("_")[0]
    name2=logs[1].split("_")[0]
    times1,perf1=autoread(logs[0],yname)
    times2,perf2=autoread(logs[1],yname)

    diff = len(times1) - len(times2)
    if (diff >0):
        add=[0]*diff
        add.extend(perf2)
        times2=times1
        perf2=add
    elif (diff<0):
        add=[0]*(0-diff)
        add.extend(perf1)
        times1=times2
        perf1=add

    plt.plot( times1,perf1,'r-^',label=name1,linewidth=2.0)
    plt.plot( times2,perf2,'b-o',label=name2,linewidth=2.0)
        
    plt.grid()
    plt.xticks(fontsize=18)
    plt.yticks(fontsize=18)

    plt.xlabel('Time(s)', fontsize=20)
    plt.ylabel(yname, fontsize=20)
    plt.legend()
    
    #save figure as fname
    fname=  yname.split("(")[0]
    plt.savefig(fname+'.pdf')  #save figure as fname
    #plt.savefig(name+'.png')  #save figure as fname
    plt.show()           #show the figure
    plt.close()

'''
main function: scan the files in current directory, find scv files and plot their data
'''
if __name__=="__main__":
    filenames=os.listdir(os.getcwd())  #get file names in current directory
    bw_logs=[]
    clat_logs=[]
    slat_logs=[]
    lat_logs=[]
    
    for fn in filenames:
        if fn.endswith("_bw.1.log"):
            bw_logs.append(fn)
            print fn
        elif fn.endswith("_clat.1.log"):
            clat_logs.append(fn)
            print fn
        elif fn.endswith("_slat.1.log"):
            slat_logs.append(fn)
            print fn
        elif fn.endswith("_lat.1.log"):
            lat_logs.append(fn)
            print fn
    plotline(bw_logs, "Throughput(MB/s)")
##    plotline(clat_logs,"Completion  Latency(ms)")
##    plotline(slat_logs,"Submission  Latency(ms)")
    plotline(lat_logs,"Total Latency(ms)")
