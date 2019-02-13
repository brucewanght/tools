#coding=utf-8

'''
This script is used to process the log files produced by db_bench in RocksDB or LevelDB
First, create a sub-directory named "log" in current directory this script in;
Then, put those log files in this log directory
Finally, run this script, and the result csv files and images (or pdfs) will generated in the img directory
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

bench = ['fillseq','fillrandom','readseq','readrandom','updaterandom','overwrite']          #benchmarks
values = ['16','64','256','1024','4096','16384']                                            #value size(Byte)
system = ['perflog_sync1_ext4','perflog_sync1_btrfs','perflog_sync1_xfs','perflog_sync1_bluefs','perflog_sync1_rocksfs']  #file systems

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

#create the csv files of fata from log files
def createCsv():
    if (os.path.isdir('csv')):
        shutil.rmtree('csv')
    os.makedirs('csv')

    for i in range(len(param)):
        for j in range(len(bench)):
            lat_a = []
            ops_a = []
            med_a = []
            p99_a = []
            for k in range(len(system)):
                for l in range(len(values)):
                    #generate the proper path of log files 
                    path = 'log/'+system[k]+'/'+ bench[j] +'_'+values[l]+'.log'
                    fp = open(path,'r')
                    #read the content of file
                    content = fp.read()
                    #get needed data through Regular Expression, includding latency, ops, median and p99
                    latP = re.compile(r'\w+\.\w+(?=\smicros/op\b)')
                    opsP = re.compile(r'(?<=\bop\s)\w+\b')
                    medP = re.compile(r'(?<=\bMedian:\s)\d+\.\d*|0\.\d*[1-9]\d*$')
                    p99P = re.compile(r'(?<=\bP99:\s)\d+\.\d*|0\.\d*[1-9]\d*$')
                    if (i==0):
                        ops = int(opsP.findall(content)[0])
                        ops_a.append(ops)
                    elif (i==1):
                        lat = round(float(latP.findall(content)[0]),2)
                        lat_a.append(lat)
                    elif (i==2):
                        med = round(1000000/float(medP.findall(content)[0]),2)
                        med_a.append(med)
                    elif (i==3):
                        p99 = round(1000000/float(p99P.findall(content)[0]),2)
                        p99_a.append(p99)

            #write data to csv files, each line corresponding to a filesystem
            #and every line has 6 data
            filename = 'csv/'+bench[j]+' '+param[i]+'.csv'
            if i==0:
                for u in range(0,30):
                    if u%6==5:
                        fr = open(filename,'a+')
                        fr.write(str(ops_a[u])+'\n')
                        fr.close()
                    else:
                        fr = open(filename,'a+')
                        fr.write(str(ops_a[u])+',')
                        fr.close()
            elif i==1:
                for u in range(0,30):
                    if u%6==5:
                        fr = open(filename,'a+')
                        fr.write(str(lat_a[u])+'\n')
                        fr.close()
                    else:
                        fr = open(filename,'a+')
                        fr.write(str(lat_a[u])+',')
                        fr.close()
            elif i==2:
                for u in range(0,30):
                    if u%6==5:
                        fr = open(filename,'a+')
                        fr.write(str(med_a[u])+'\n')
                        fr.close()
                    else:
                        fr = open(filename,'a+')
                        fr.write(str(med_a[u])+',')
                        fr.close()
            elif i==3:
                for u in range(0,30):
                    if u%6==5:
                        fr = open(filename,'a+')
                        fr.write(str(p99_a[u])+'\n')
                        fr.close()
                    else:
                        fr = open(filename,'a+')
                        fr.write(str(p99_a[u])+',')
                        fr.close()
    fp.close()
#end of createCsv
    
#create images from data files
def createImg():
    if (os.path.isdir('img')):
        shutil.rmtree('img')
    os.makedirs('img')
    for l in range(len(bench)):
        for k in range(len(param)):
            path = 'csv/'+ bench[l] +' '+param[k]+'.csv'
            #read data from csv files to array data
            data=[]
            data=readCsv(path)
            #L=[[float (x) for x in y.split(',')] for y in open(path).read().rstrip().split('\n')[0:]]
            #nomilize data by data[0]
            normal=data[0][:]
            for i in range(0,5):
                for j in range(0,6):
                    data[i][j]=float(data[i][j])/float(normal[j])

            N=6
            ind = np.arange(N)       #the x locations for the groups
            total_width, n = 0.8, 5  #total width of bar group and number of bars in every group
            width = total_width / n #the width of bar

            #plot every data group, use different shapes to fill bars
            fig, ax = plt.subplots()
            rects1 = ax.bar(ind, data[0], width, label="Ext4")
            rects2 = ax.bar(ind + width, data[1], width,label="Btrfs",hatch='.')
            rects3 = ax.bar(ind + 2*width, data[2], width,label="XFS",hatch='X')
            rects4 = ax.bar(ind + 3*width, data[3], width,label="BlueFS", hatch='\\')
            rects5 = ax.bar(ind + 4*width, data[4], width, label="RocksFS",hatch='/')
    
            # add some text for labels, title and axes ticks
            ax.set_ylabel('Normalized IOPS')
            ax.set_xlabel('Value Size')
            ax.set_xticks(ind + 2*width)
            ax.set_xticklabels(('16B', '64B','256B','1K', '4K', '16K'))

            #set legends for bars
            ax.legend((rects1[0], rects2[0],rects3[0],rects4[0],rects5[0]), ('Ext4', 'Btrfs', 'XFS', 'BlueFS', 'RocksFS'))
            if "read" in path:
                ax.legend(loc='lower right')
            ax.grid(True)       #show grid
            plt.savefig('img/'+bench[l]+' '+param[k]+'.png')
            plt.close()
#end of createImg

'''
main function: create scv files and plot their data
'''
if __name__=="__main__":
    createCsv()
    createImg()
    #get the end time of this script
    end = time.time()
    #print the time consumed by this script
    print("Run Time (seconds): %f", end-start)
