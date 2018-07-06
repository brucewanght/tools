#coding=utf-8
"""
========
Note:
1.This is for "iotop -o -k -b" command output log
2.Example data as follow: 
========
PID:4630,4631,4632
Total DISK READ :  132071.10 K/s | Total DISK WRITE :       0.00 K/s
Actual DISK READ:  132071.10 K/s | Actual DISK WRITE:       2.39 K/s
  TID  PRIO  USER     DISK READ  DISK WRITE  SWAPIN      IO    COMMAND
 1327 be/4 root     20738.02 K/s    0.00 K/s  0.00 %  0.00 % dd if=/dev/sdb1 of=/dev/null bs=4K
 1328 be/4 root     41526.99 K/s    0.00 K/s  0.00 %  0.00 % dd if=/dev/sdb2 of=/dev/null bs=4K
 1329 be/4 root     69806.10 K/s    0.00 K/s  0.00 %  0.00 % dd if=/dev/sdb3 of=/dev/null bs=4K
Total DISK READ :  126648.43 K/s | Total DISK WRITE :       0.00 K/s
Actual DISK READ:  126648.43 K/s | Actual DISK WRITE:       0.00 K/s
  TID  PRIO  USER     DISK READ  DISK WRITE  SWAPIN      IO    COMMAND
    8 be/4 root        0.00 K/s    0.00 K/s  0.00 % 99.99 % [ksoftirqd/0]
 1327 be/4 root     21010.45 K/s    0.00 K/s  0.00 %  0.00 % dd if=/dev/sdb1 of=/dev/null bs=4K
 1328 be/4 root     38964.83 K/s    0.00 K/s  0.00 %  0.00 % dd if=/dev/sdb2 of=/dev/null bs=4K
 1329 be/4 root     66673.16 K/s    0.00 K/s  0.00 %  0.00 % dd if=/dev/sdb3 of=/dev/null bs=4K
"""
import csv
import os
import numpy as np
import matplotlib.pyplot as plt
import linecache


#              red       orange     green       blue        pink     brown      purple
defcolors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#e377c2', '#8c564b', '#9467bd']
deflinestyle = ['-o','-v','-s','-p','-^','-+']
defhatchs = ['-', '+', 'x', '\\', '*', 'o', '.']

'''
autoread: read data form  file to list 
filename: collectl log file name
blkname: block names we care about
'''
def autoread(filename, pids):
    with open(filename, 'r') as f:
        data = f.readlines()
    perfs=[[] for i in range(len(pids))]
    for line in data:
        sline = line.strip()     #remove multiple blank spaces between numbers
        nums = sline.split()     #split data with blank space 
        for i in range(0,len(pids)):
            if sline.startswith(pids[i]):
                #the 4th and 5th number is IO throughput in KB/s, we convert it to MB/s
                throughput = (float(nums[3])+float(nums[5]))/1000 
                perfs[i].append(throughput)
    return perfs

'''
plotdata: plot data to line chart
logs: data log names
xname: x-axis name
yname: y-axis name
kwargs: some other parameters
'''
def plotline(log, pids, xname, yname, **kwargs):
    styles = kwargs.get('styles', deflinestyle)
    #plt.style.use('seaborn-whitegrid')
    plt.figure(dpi=300, figsize=(10, 6))
    perfs = autoread(log, pids)             #get performance data for pids
    avgperfs = []
    #avgperfs = np.mean(perfs, axis=1)       #get the mean value of every line (i.e., every pid)
   

    for i in range(0,len(perfs)):
        lname='tenant-'+str(i)
        avgperf = np.mean(perfs[i])
        avgperfs.append(avgperf)
        ls=styles[i]
        perf=perfs[i]
        time=[t*5 for t in range(0,len(perf))]  #time interval is 5 seconds
        plt.plot(time, perf, ls, label=lname, linewidth=2.0)

    stdavg = avgperfs/avgperfs[0]
    xmax = len(perfs[0])
    print(avgperfs)
    print(stdavg)
    #plt.ylim(0,1000)
    plt.xlim(0,xmax*5)

    plt.grid()
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)

    plt.xlabel(xname, fontsize=20)
    plt.ylabel(yname, fontsize=20)
    #plt.legend()
    #plt.legend(loc='center right',ncol=1,fancybox=True,shadow=True,prop = {'size':16})
    plt.legend(bbox_to_anchor=(0.00, 1.01, 1.00, 1.01 ), loc=3, ncol=5, mode="expand", borderaxespad=0., prop = {'size':24})
    #plt.legend(loc='best',ncol=1,fancybox=True,shadow=True,prop = {'size':16})

    pname = log.split(".")[0]
    plt.savefig(pname+".pdf", bbox_inches='tight')  # save figure as pdf file, and make it tight
    plt.savefig(pname+".png", bbox_inches='tight')  # save figure as jpg file, and make it tight
    #plt.show()  # show the figure
    plt.close()


'''
main function: scan the files in current directory, find log files and plot their data
'''
if __name__ == "__main__":
    filenames = os.listdir(os.getcwd())  # get file names in current directory
    bw_logs = []
    pids = []

    for fn in filenames:
        if fn.endswith(".perf"):
            first_line = linecache.getline(fn,1).strip()    #read the first line of the file and remove unnecessary blanks
            if first_line.startswith("PID"):
                user_pids = first_line.split(":")[1].split(",") #get the pids
                bw_logs.append(fn)
                pids.append(user_pids)
            else:
                print("Performance file is incorrect, the first line should be pids, e.g.:")
                print("PID:30731,30732,30733")

    for i in range(0,len(bw_logs)):
        plotline(bw_logs[i], pids[i], "time(s)","Throughput(MB/s)")
