#coding=utf-8
"""
========
Note:
1.This is for "collectl -sD" command output log
2.Example data as follow: 
========
# DISK STATISTICS (/sec)
#          <---------reads---------------><---------writes--------------><--------averages--------> Pct
#Name       KBytes Merged  IOs Size  Wait  KBytes Merged  IOs Size  Wait  RWSize  QLen  Wait SvcTim Util
sda            102      0    1  128     0       8      1    0   20     0      92     0     0      0    0
sdb              0      0    0    0     0       0      0    0    0     0       0     0     0      0    0
sdc          26404   2858  611   43    54       0      0    0    0     0      43    34    54      1   96
nvme1n1          0      0    0    0     0       0      0    0    0     0       0     0     0      0    0
sdd          19870    979 2055   10    34       0      0    0    0     0       9    72    34      0   98
sde          13556    802  676   20    27       0      0    0    0     0      20    21    27      1   86
sdf          19172    842  792   24    89       0      0    0    0     0      24    71    89      1   99
nvme0n1          0      0    0    0     0       0      0    0    0     0       0     0     0      0    0
nvme2n1          0      0    0    0     0       0      0    0    0     0       0     0     0      0    0
dm-0         97005      0  24K    4     4       0      0    0    0     0       4   115     4      0   99
dm-1         87211      0  21K    4     5       0      0    0    0     0       4   116     5      0   99
dm-2        251608      0  62K    4     1       0      0    0    0     0       4    92     1      0   99
dm-3          5476      0 1369    4    92       0      0    0    0     0       4   127    92      0   99
"""
import csv
import os
import numpy as np
import matplotlib.pyplot as plt


#              red       orange     green       blue        pink     brown      purple
defcolors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#e377c2', '#8c564b', '#9467bd']
deflinestyle = ['-o','-v','-s','-p','-^','-+']
defhatchs = ['-', '+', 'x', '\\', '*', 'o', '.']

'''
autoread: read data form  file to list 
filename: collectl log file name
blkname: block names we care about
'''
def autoread(filename, blknames):
    with open(filename, 'r') as f:
        data = f.readlines()
    perfs=[[] for i in range(len(blknames))]
    for line in data:
        line.strip()            #remove multiple blank spaces between numbers
        nums = line.split()     #split data with blank space 
        for i in range(0,len(blknames)):
            if line.startswith(blknames[i]):
                throughput = float(nums[1])/1000  #the second number is throughput in KB/s
                perfs[i].append(throughput)
    return perfs

'''
plotdata: plot data to line chart
logs: data log names
xname: x-axis name
yname: y-axis name
kwargs: some other parameters
'''
def plotline(log, blknames, xname, yname, **kwargs):
    styles = kwargs.get('styles', deflinestyle)
    #plt.style.use('seaborn-whitegrid')
    plt.figure(dpi=300, figsize=(10, 8))
    perfs = autoread(log, blknames)             #get performance data for blknames

    agg_perf=[0]*len(perfs[0])                  #aggregated performance of all tenants
    time=[t*10 for t in range(0,len(perfs[0]))] #time interval is 10 seconds

    for i in range(0,len(perfs)):
        lname='tenant-'+str(i)
        ls=styles[i]
        perf=perfs[i]
        plt.plot(time, perf, ls, label=lname, linewidth=2.0)
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

    pname = log.split(".")[0]
    plt.savefig(pname+".pdf")  # save figure as fname
    plt.show()  # show the figure
    plt.close()


'''
main function: scan the files in current directory, find log files and plot their data
'''
if __name__ == "__main__":
    filenames = os.listdir(os.getcwd())  # get file names in current directory
    bw_logs = []
    blknames = ['dm-0','dm-1','dm-2','dm-3']

    for fn in filenames:
        if fn.endswith(".perf"):
            bw_logs.append(fn)
            print(fn)

    for log in bw_logs:
        plotline(log, blknames, "time(s)","Throughput(MB/s)")
