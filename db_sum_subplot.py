#coding=utf-8

'''
This script is used to process the csv files produced by db_sum.py.
Plot subfigures according to those csv files.
'''
import os
import shutil
import re
import csv
import time
import numpy as np
import matplotlib.pyplot as plt
import sys

#record the start time of thie script
start = time.time()

#              red       orange     green       blue        pink     brown      purple
defcolors = ['#d62728', '#ff7f0e', '#2ca02c', '#1f77b4', '#e377c2', '#8c564b', '#9467bd']
deflinestyle = ['-o','-v','-s','-p','-^','-+']
defhatchs = ['-', '.', 'x', '\\', '*', '/', '+']

bench = ['fillseq','fillrandom','updaterandom','overwrite','readseq','readrandom'] #benchmarks
values = ['16','64','256','1024','4096','16384']    #value size(Byte)
system = ['ext4','btrfs','xfs','bluefs','rocksfs']  #file systems

#set parameters we want to extract
param = ['iops','lat','med','p99']
cparam = ['IOPS','LAT','MED','P99']

'''
readCsv: read data form csv file to list 
'''
def readCsv(path):
    data=[]
    csvfile_in = open(path, 'r')
    reader = csv.reader(csvfile_in)
    for line in reader:
        data.append(line)
    csvfile_in.close()
    return data
#end of readCsv

'''
plot_bar: plot bar chart
sub: sub plot ax
kwargs: some other parameters
'''
def plot_bar(data, sub, fig_title, has_legend, **kwargs):
    #plt.style.use('seaborn-whitegrid')
    hatchs = kwargs.get('hatchs', defhatchs)
    colors = kwargs.get('colors', defcolors)
    ind = np.arange(len(values))           #the x locations for the groups
    total_width, n = 0.8, (len(values)-1)  #total width of bar group and number of bars in every group
    width = total_width / n #the width of bar

    if has_legend == 1:
        for i in range(0,len(system)):
            sub.bar(ind+i*width, data[i], width, color=colors[i], hatch=hatchs[i], label=system[i])
            sub.set_xticks(ind + 2*width)
            sub.set_xticklabels(('16B', '64B','256B','1K', '4K', '16K'))
    else:
        for i in range(0,len(system)):
            sub.bar(ind+i*width, data[i], width, color=colors[i], hatch=hatchs[i]) 
            sub.set_xticks(ind + 2*width)
            sub.set_xticklabels(('16B', '64B','256B','1K', '4K', '16K'))

    sub.set_title(fig_title, size=20)
    sub.tick_params(labelsize=20) 
    sub.grid()
#end of plot_bar
  
#create images from data files
def createImg():
    if (os.path.isdir('subplot_img')):
        shutil.rmtree('subplot_img')
    os.makedirs('subplot_img')

    for l in range(len(param)):
        #create a figure that has 3 sub-figures in one row, and they share x-axis
        fig, axes = plt.subplots(nrows=2, ncols=3, sharex=True, figsize=(16,10))
        fig_seqs = ['(a)','(b)','(c)','(d)','(e)','(f)']
        for k in range(len(bench)):
            path = 'csv/'+ bench[k] +' '+param[l]+'.csv'
            #read data from csv files to array data
            data=[]
            data=readCsv(path)
            #nomilize data by data[0]
            normal=data[0][:]
            for i in range(0,5):
                for j in range(0,6):
                    data[i][j]=float(data[i][j])/float(normal[j])
    
            if k == 0:
                plot_bar(data, axes[k//3][k%3], fig_seqs[k]+bench[k], 1)
            else:
                plot_bar(data, axes[k//3][k%3], fig_seqs[k]+bench[k], 0)

        axes[0][0].set_ylabel('Normalized IOPS', size=20)
        axes[1][0].set_ylabel('Normalized IOPS', size=20)
        axes[1][1].set_xlabel('Value Size',size=20)
        axes[0][0].legend(bbox_to_anchor=(0.00, 1.15, 3.20, 1.15), loc=3, ncol=5, mode="expand", borderaxespad=0., prop = {'size':24})
        fig.tight_layout()
        #plt.show()
        #save figure as pdf file, and make it tight
        fig.savefig('subplot_img/'+param[l]+'.pdf',  bbox_inches='tight', dpi=400)
        #plt.savefig('subplot_img/'+param[l]+'.png')
        plt.close()
#end of createImg

'''
main function: create scv files and plot their data
'''
if __name__=="__main__":
    createImg()
    #get the end time of this script
    end = time.time()
    #print the time consumed by this script
    print("Run Time (seconds):", end-start)
