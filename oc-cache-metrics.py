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
npoint: number of points to be processed
'''
def get_metrics(logs, blknames, npoint):
    tenant_th=[]
    tenant_st=[]
    #open a csv file, the newline parameter is used to get rid of empty lines   
    th_out = open('throughput.csv','w',newline='')
    rs_out = open('stablity.csv','w',newline='')

    th_csv = csv.writer(th_out)
    rs_csv = csv.writer(rs_out)

    th_csv.writerow(["tenant-0","tenant-1","tenant-2","tenant-3","aggregate"])
    rs_csv.writerow(["tenant-0","tenant-1","tenant-2","tenant-3","aggregate"])

    for log in logs:
        #open log file and read all the strings to data
        with open(log, 'r') as f:
            data = f.readlines()

        perfs=[[] for i in range(len(blknames))]
        avg_perfs =[ 0 for i in range(len(blknames))]
        stablity_perfs =[ 0 for i in range(len(blknames))]

        count = 0
        #we get those specified performance numbers and store them in list perfs
        for line in data:
            line.strip()  # remove multiple blank spaces between numbers
            nums = line.split()  # split data with blank space
            if (count >= 4*npoint):
                break
            count = count+1
            for i in range(0, len(blknames)):
                if line.startswith(blknames[i]):
                    #the 2nd and 6th number is read and write throughput in KB/s
                    throughput = (float(nums[1])+float(nums[6]))/1000
                    perfs[i].append(throughput)

        #get average performance data
        for i in range(0, len(perfs)):
            #avg_perfs[i] = sum(perfs[i])/len(perfs[i])
            avg_perfs[i] = np.mean(perfs[i])
            stablity_perfs[i] = np.std(perfs[i], ddof = 1)/avg_perfs[i]
        
        #store average performance list to result list
        tenant_th.append(avg_perfs)
        tenant_st.append(stablity_perfs)

    #write average performance data to csv file
    th_csv.writerows(tenant_th)
    rs_csv.writerows(tenant_st)
    th_out.close()
    rs_out.close()
    return tenant_th, tenant_st

'''
plotdata: plot data to line chart
logs: data log names
xname: x-axis name
yname: y-axis name
kwargs: some other parameters
'''
def plotbar(avg_perfs, blknames, xname, yname, figname, **kwargs):
    #plt.style.use('seaborn-whitegrid')
    hatchs = kwargs.get('hatchs', defhatchs)
    labels = ['tenant-0','tenant-1','tenant-2','tenant-3']
    xlabels = ['Shared-Cache','OC-Cache']

    fig, ax = plt.subplots(figsize=(7,9))

    t0 = [avg_perfs[0][0], avg_perfs[1][0]]
    t1 = [avg_perfs[0][1], avg_perfs[1][1]]
    t2 = [avg_perfs[0][2], avg_perfs[1][2]]
    t3 = [avg_perfs[0][3], avg_perfs[1][3]]

    bar_width = 0.5
    bottom2 = [i+j for i,j in zip(t0, t1)]
    bottom3 = [i+j for i,j in zip(bottom2, t2)]

    ax.bar(xlabels, t0, width=bar_width, hatch=hatchs[0], label=labels[0])
    ax.bar(xlabels, t1, bottom=t0, width=bar_width, hatch=hatchs[1], label=labels[1])
    ax.bar(xlabels, t2, bottom=bottom2, width=bar_width, hatch=hatchs[2], label=labels[2])
    ax.bar(xlabels, t3, bottom=bottom3, width=bar_width, hatch=hatchs[3], label=labels[3])

    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width, box.height*0.8])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.20), ncol=2,fancybox=True, shadow=True, prop = {'size':20})

    #set the location of xticks and xlabels
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    #plt.legend(loc='upper center',ncol=2,fancybox=True,shadow=True, prop = {'size':18})
    plt.ylabel(yname, fontsize=20)
    plt.grid()
    plt.show()  # show the figure
    fig.savefig(figname+".pdf", bbox_inches='tight')  # save figure as fname
    plt.close()


'''
main function: scan the files in current directory, find log files and plot their data
'''
if __name__ == "__main__":
    cwd = os.getcwd()            # get current wording directory
    filenames = os.listdir(cwd)  # get file names in current directory
    figname = cwd.split('_')[-1] # get the last string splited by "-"
    bw_logs = []
    avg_perfs = []
    stablity_perfs = []
    blknames = ['dm-0','dm-1','dm-2','dm-3']

    for fn in filenames:
        if fn.endswith(".perf"):
            bw_logs.append(fn)
            print(fn)

    avg_perfs,stablity_perfs = get_metrics(bw_logs, blknames, 150)
    print(avg_perfs)
    print(stablity_perfs)
    plotbar(avg_perfs, blknames, "tenant","Throughput (MB/s)", "throughput-"+figname)
    plotbar(stablity_perfs, blknames, "tenant","Stablity", "stablity-"+figname)