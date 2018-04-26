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
logs: collectl log file names
blkname: block names we care about
'''
def get_avg_perf(logs, blknames):
    result=[]
    #open a csv file, the newline parameter is used to get rid of empty lines   
    csvfile_out = open('average-throughput.csv','w',newline='')
    f_csv = csv.writer(csvfile_out)

    for log in logs:
        #open log file and read all the strings to data
        with open(log, 'r') as f:
            data = f.readlines()

        perfs=[[] for i in range(len(blknames))]
        avg_perfs =[ 0 for i in range(len(blknames))]


        #we get those specified performance numbers and store them in list perfs
        for line in data:
            line.strip()  # remove multiple blank spaces between numbers
            nums = line.split()  # split data with blank space
            for i in range(0, len(blknames)):
                if line.startswith(blknames[i]):
                    #the 2nd and 6th number is read and write throughput in KB/s
                    throughput = (float(nums[1])+float(nums[6]))/1000
                    perfs[i].append(throughput)

        #get average performance data
        for i in range(0, len(perfs)):
            avg_perfs[i] = sum(perfs[i])/len(perfs[i])
        
        #store average performance list to result list
        result.append(avg_perfs)

    #write average performance data to csv file
    f_csv.writerows(result)
    csvfile_out.close()
    return result

'''
plotdata: plot data to line chart
logs: data log names
xname: x-axis name
yname: y-axis name
kwargs: some other parameters
'''
def plotbar(avg_perfs, blknames, xname, yname, **kwargs):
    #plt.style.use('seaborn-whitegrid')
    hatchs = kwargs.get('hatchs', defhatchs)
    xtocklabels = ['tenant-0','tenant-1','tenant-2','tenant-3']
    labels = ['Shared-Cache','OC-Cache']

    size = len(xtocklabels)
    x = np.arange(size)
    total_width, n = 0.8, 2  #total width of bar group and number of bars in every group
    width = total_width/n #the width of bar
    fig, ax = plt.subplots(figsize=(8,6))

    plt.bar(x, avg_perfs[0], width=width, alpha=0.5, color='b', hatch=hatchs[5], label=labels[0])
    plt.bar(x+width, avg_perfs[1], width=width, alpha=0.5, color='r', hatch=hatchs[6], label=labels[1])

    #set the location of xticks and xlabels
    ax.set_xticks(x+width/2) 
    ax.set_xticklabels(xtocklabels, fontsize=20)

    plt.yticks(fontsize=20)
    plt.ylim(0,320)
    plt.legend(loc='upper center',ncol=2,fancybox=True,shadow=True, prop = {'size':18})
    plt.ylabel(yname, fontsize=20)
    plt.grid()
    plt.show()  # show the figure
    fig.savefig("average-throughput-bar.pdf", bbox_inches='tight')  # save figure as fname
    plt.close()


'''
main function: scan the files in current directory, find log files and plot their data
'''
if __name__ == "__main__":
    filenames = os.listdir(os.getcwd())  # get file names in current directory
    bw_logs = []
    avg_perfs = []
    blknames = ['dm-0','dm-1','dm-2','dm-3']

    for fn in filenames:
        if fn.endswith(".perf"):
            bw_logs.append(fn)
            print(fn)

    avg_perfs = get_avg_perf(bw_logs, blknames)
    plotbar(avg_perfs, blknames, "tenant","Throughput(MB/s)")