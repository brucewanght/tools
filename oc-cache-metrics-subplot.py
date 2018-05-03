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
defhatchs = ['-', '.', 'x', '\\', '*', '/', '+']

'''
autoread: read data form  file to list 
logs: collectl log file names
blkname: block names we care about
nbegin: begin number of point
nend: end number of point
'''
def get_metrics(logs, blknames, nbegin, nend):
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
            if (count < 4*nbegin):
                count = count+1
                continue
            if (count >= 4*nend):
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
            stablity_perfs[i] = avg_perfs[i]/np.std(perfs[i], ddof = 1)
        
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
plot_stackbar: plot stacked bar chart
sub: sub plot ax
kwargs: some other parameters
'''
def plot_stackbar(avg_perfs, sub, **kwargs):
    #plt.style.use('seaborn-whitegrid')
    hatchs = kwargs.get('hatchs', defhatchs)
    colors = kwargs.get('colors', defcolors)
    labels = ['tenant-0','tenant-1','tenant-2','tenant-3']
    xlabels = ['OC-Cache','Shared-Cache']

    t0 = [avg_perfs[0][0], avg_perfs[1][0]]
    t1 = [avg_perfs[0][1], avg_perfs[1][1]]
    t2 = [avg_perfs[0][2], avg_perfs[1][2]]
    t3 = [avg_perfs[0][3], avg_perfs[1][3]]

    bar_width = 0.5
    bottom2 = [i+j for i,j in zip(t0, t1)]
    bottom3 = [i+j for i,j in zip(bottom2, t2)]

    sub.bar(xlabels, t0, width=bar_width, color=colors[0], hatch=hatchs[0], label=labels[0])
    sub.bar(xlabels, t1, bottom=t0, width=bar_width, color=colors[1], hatch=hatchs[1], label=labels[1])
    sub.bar(xlabels, t2, bottom=bottom2, width=bar_width, color=colors[2], hatch=hatchs[2], label=labels[2])
    sub.bar(xlabels, t3, bottom=bottom3, width=bar_width, color=colors[3], hatch=hatchs[3], label=labels[3])
    sub.grid()

'''
plot_bar: plot bar chart
sub: sub plot ax
kwargs: some other parameters
'''
def plot_bar(avg_perfs, sub, **kwargs):
    #plt.style.use('seaborn-whitegrid')
    hatchs = kwargs.get('hatchs', defhatchs)
    colors = kwargs.get('colors', defcolors)
    xlabels = ['OC-Cache','Shared-Cache']
    bar_width = 0.5 
    sub.bar(xlabels[0], avg_perfs[0], bar_width, color=colors[5], hatch=hatchs[5])
    sub.bar(xlabels[1], avg_perfs[1], bar_width, color=colors[6], hatch=hatchs[6])
    sub.grid()

'''
main function: scan the files in current directory, find log files and plot their data
'''
if __name__ == "__main__":
    cwd = os.getcwd()            #get current wording directory
    filenames = os.listdir(cwd)  #get file names in current directory
    figname = cwd.split('_')[-1] #get the last string splited by "-"
    bw_logs = []                 #performance logs
    avg_perfs = []               #average performance
    stablity_perfs = []          #stablity of performance
    util = []                    #utilization of oc-cache and shared-cache
    blknames = ['dm-0','dm-1','dm-2','dm-3']
    titles = ['OC-Cache','Shared-Cache']
    w_ratio=[]             #write ratios of tenants
    cache_bandwidth = 0    #cache bandwidth
    br = 300               #read bandwidth
    bw = 223               #write bandwidth

    #get names of performance files and configure file
    for fn in filenames:
        if fn.endswith(".perf"):
            bw_logs.append(fn)
        elif fn.endswith(".conf"):
            conf = fn

    #parse the configure file
    with open(conf, 'r') as f:
        data = f.readlines()
    for line in data:
        if "dev" in line:
            line.strip()              #remove multiple blank spaces between numbers
            p_list = line.split(",")  #split data with comma
            #the last element is write ratio
            w_ratio.append(int(p_list[-1]))
            print(p_list)
    #calculate the cache bandwidth
    for wr in w_ratio:
        if wr==0:
            cache_bandwidth = cache_bandwidth + br
        else:
            cache_bandwidth = cache_bandwidth + br*(1-wr/100) + bw*wr/100

    #get performance metric data
    avg_perfs,stablity_perfs = get_metrics(bw_logs, blknames, 0, 1800)
    oc_sum = sum(avg_perfs[0])
    shared_sum = sum(avg_perfs[1])
    oc_stability = sum(stablity_perfs[0])
    shared_stability = sum(stablity_perfs[1])
    oc_uti = oc_sum/cache_bandwidth*100
    shared_uti = shared_sum/cache_bandwidth*100
    util.append(oc_uti)
    util.append(shared_uti)
    print("         cache bandwidth: "+str(cache_bandwidth)+" MB/s")
    print("    oc-cache utilization: "+str(oc_uti)+" %")
    print("shared-cache utilization: "+str(shared_uti)+" %")
    print(" performance improvement: "+str((oc_sum-shared_sum)/shared_sum*100)+" %")
    print("    stablity improvement: "+str((oc_stability-shared_stability)/shared_stability*100)+" %")
    print(" utilization improvement: "+str(oc_uti-shared_uti)+" %")

    #create a figure that has 2 sub-figures in one row, and they share x-axis and y-axis
    fig, axes = plt.subplots(nrows=1, ncols=3,sharex=True, figsize=(14,9))
    #draw every sub-figures
    plot_stackbar(avg_perfs, axes[0])
    plot_stackbar(stablity_perfs, axes[1])
    plot_bar(util, axes[2])
    axes[0].set_title("(a)Throughput (MB/s)", size=20)
    axes[1].set_title("(b)Stability", size=20)
    axes[2].set_title("(c)Utilization (%)", size=20)
   
    #set tick size to 20
    for ax in axes:
        ax.tick_params(labelsize=20)  

    axes[0].legend(loc='lower left', ncol=1,fancybox=True, shadow=True, prop = {'size':20})
    fig.tight_layout()
    #plt.show()
    fig.savefig("performance-"+figname+".pdf", bbox_inches='tight')  # save figure as pdf file, and make it tight