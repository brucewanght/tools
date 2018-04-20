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
#              red       orange     green       blue        pink     brown      purple
defcolors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#e377c2', '#8c564b', '#9467bd']
deflinestyle = ['-o','-v','-s','-p','-^','-+']
defhatchs = ['-', '+', 'x', '\\', '*', 'o', '.']

def autoread(filename):
    perf = []
    csvfile_in = open(filename, 'r')
    reader = csv.reader(csvfile_in)
    for line in reader:
        perf_value = float(line[0])
        perf.append(perf_value)
    return perf

'''
plotdata: plot data to line chart
'''
def plotline(logs, xname, yname, **kwargs):
    styles = kwargs.get('styles', deflinestyle)
    #plt.style.use('seaborn-whitegrid')
    plt.figure(dpi=300, figsize=(10, 8))
    perfs=[]
    names=[]
    for log in logs:
        temp = log.split("-")[1]
        id = temp.split("_")[0]
        name="tenant-"+id
        perf = autoread(log)
        perfs.append(perf)
        names.append(name)

    agg_perf=[0]*len(perfs[0])           #aggregated performance of all tenants
    time=[t*10 for t in range(0,len(perfs[0]))] #time interval is 10 seconds

    for i in range(0,len(perfs)):
        ls=styles[i]
        perf=perfs[i]
        plt.plot(time, perf, ls, label=names[i], linewidth=2.0)
        for j in range(0,len(perf)):
            agg_perf[j]=agg_perf[j]+perf[j]

    plt.ylim(0,1100)
    plt.xlim(0,1600)
    plt.plot(time, agg_perf,'-^', label='Aggregated', linewidth=2.0)

    plt.grid()
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    plt.xlabel(xname, fontsize=20)
    plt.ylabel(yname, fontsize=20)
    #plt.legend()
    plt.legend(loc='upper left',ncol=1,fancybox=True,shadow=True,prop = {'size':16})

    plt.savefig('throughput-curve.pdf')  # save figure as fname
    #plt.savefig(name+'.png')  #save figure as fname
    plt.show()  # show the figure
    plt.close()


'''
main function: scan the files in current directory, find scv files and plot their data
'''
if __name__ == "__main__":
    filenames = os.listdir(os.getcwd())  # get file names in current directory
    bw_logs = []
    clat_logs = []
    slat_logs = []
    lat_logs = []

    for fn in filenames:
        if fn.endswith("_bw"):
            bw_logs.append(fn)
            print(fn)
    plotline(bw_logs, "time(s)","Throughput(MB/s)")
