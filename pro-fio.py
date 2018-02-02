#coding:UTF-8
import csv
import os
import time

#注意:
#本程序编写的时候使用的是python 2.7.10，如果测试环境python版本高于2.7可能会有问题
#使用该程序的时候，测试的原始数据需要保存为指定格式，即以fio+测试编号，如fio-11
#需要处理的数据与该程序要放在同一目录,并且同一目录下没有其他以fio开头的非测试数据文件
#建议的使用方法是先用shell脚本fiotest.sh生成原始测试数据，然后直接运行该脚本生成最终结果

#测试编号约定：fio-a-b
#a:读写模式，sw表示顺序写，sr表示顺序读，rw表示随机写，rr表示随机读
#b:io块大小，支持4k，16k，64k，256k，1024k，4096k
#示例：fio-23表示IO块为8K的随机读测试

#能够处理的fio测试的原始数据格式如下:
'''
t11: (g=0): rw=read, bs=4K-4K/4K-4K/4K-4K, ioengine=psync, iodepth=1
fio-2.1.3
Starting 1 thread

t11: (groupid=0, jobs=1): err= 0: pid=1037: Mon Sep 12 09:58:25 2016
  read : io=224944KB, bw=2249.5KB/s, iops=562, runt=100001msec
    clat (usec): min=155, max=16050, avg=1769.31, stdev=400.65
     lat (usec): min=160, max=16052, avg=1771.08, stdev=400.66
    clat percentiles (usec):
     |  1.00th=[ 1400],  5.00th=[ 1464], 10.00th=[ 1496], 20.00th=[ 1576],
     | 30.00th=[ 1656], 40.00th=[ 1704], 50.00th=[ 1752], 60.00th=[ 1800],
     | 70.00th=[ 1848], 80.00th=[ 1912], 90.00th=[ 1992], 95.00th=[ 2064],
     | 99.00th=[ 2256], 99.50th=[ 3024], 99.90th=[ 7968], 99.95th=[10816],
     | 99.99th=[12992]
    bw (KB  /s): min= 1988, max= 2688, per=100.00%, avg=2250.81, stdev=173.20
    lat (usec) : 250=0.03%, 500=0.10%, 750=0.01%
    lat (msec) : 2=90.47%, 4=9.12%, 10=0.21%, 20=0.07%
  cpu          : usr=1.02%, sys=2.70%, ctx=56472, majf=0, minf=8
  IO depths    : 1=100.0%, 2=0.0%, 4=0.0%, 8=0.0%, 16=0.0%, 32=0.0%, >=64=0.0%
     submit    : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     complete  : 0=0.0%, 4=100.0%, 8=0.0%, 16=0.0%, 32=0.0%, 64=0.0%, >=64=0.0%
     issued    : total=r=56236/w=0/d=0, short=r=0/w=0/d=0

Run status group 0 (all jobs):
   READ: io=224944KB, aggrb=2249KB/s, minb=2249KB/s, maxb=2249KB/s, mint=100001msec, maxt=100001msec

Disk stats (read/write):
  vda: ios=56090/0, merge=0/0, ticks=163344/0, in_queue=96924, util=97.17%
  
'''

#处理后的数据格式如下:
'''
IO块大小	4K	16K	64K	256K	1024K	4096k	
IOPS
顺序读	562	478	463	331	163	29	
顺序写	63	59	60	70	69	24	
随机读	214	201	197	174	134	57	
随机写	93	81	92	78	73	24	
								
读写带宽(MB/s)
顺序读	2.198056641	3.740078125	7.254580078	20.75734375	20.50103516	29.20758789	
顺序写	0.24921875	0.470488281	0.94421875	4.448359375	8.711464844	24.46265625	
随机读	0.837470703	1.577304688	3.093339844	10.9171582	16.7734082	57.89740234	
随机写	0.365009766	0.639462891	1.439667969	4.912451172	9.244404297	24.4596875	
								
读写延迟(msec)
顺序读	1.76931	2.08078	2.14661	3	6.09	34.28	
顺序写	15.66	16.67	16.59	14.08	14.35	40.89	
随机读	4.65657	4.94604	5.0468	5.71912	7.44924	17.27	
随机写	10.69	12.22	10.85	12.74	13.52	40.88	

'''
#定义switch类，作用相当于c++中的switch-case语句
class switch(object):
  def __init__(self, value):
    self.value = value
    self.fall = False
  def __iter__(self):
    """Return the match method once, then stop""" 、
    yield self.match
    raise StopIteration
  def match(self, *args):
    """Indicate whether or not to enter a case suite"""
    if self.fall or not args:
      return True
    elif self.value in args:
      # changed for v1.5, see below
      self.fall = True
      return True
    else:
      return False

begin=time.time()
flist=[]
head=[]      #用于存储表头
head.append("IO块大小")
filenames=os.listdir(os.getcwd())  #获取当前目录
cdir=os.getcwd().split('\\')
result=cdir[len(cdir)-1]

for fn in filenames:
  if fn.startswith("fio-"):
     flist.append(fn)           #将待处理的文件名写入列表
flist=sorted(flist)             #将文件按照字典序进行排序

#根据文件名称与IO块的对应关系生成表头head
fl="".join(flist)
for case in switch(fl):
  if case('4k'):
    head.append("4K")
    break
  if case('16k'):
    head.append("16K")
    break
  if case('64k'):
    head.append("64K")
    break
  if case('256k'):
    head.append("256K")
    break
  if case('1024k'):
    head.append("1M")
    break
  if case('4096k'):
    head.append("4M")
    break
    
#写入csv文件
csvfile_out = file(result+".csv", 'wb')           #创建输出处理后数据的csv文件
writer = csv.writer(csvfile_out)                  #创建用于输出数据的writer
writer.writerow(head)                             #写入表头

fnum=len(flist)                   #获得待处理的文件数量
data=[[] for i in range(fnum)]    #用于存放最终的数据
iops=[[''] for i in range(4)]     #用于存放最终的IOPS数据
lat=[[''] for i in range(4)]      #用于存放最终的lat数据
mbps=[[''] for i in range(4)]     #用于存放最终的mbps数据


#处理原始数据
num=0  #记录当前打开第几个数据文件，以0开始
for fn in flist:    
    with open(fn, "r") as fin:                                     
        for line in fin:
            line=''.join(line.split())                 #去掉数据中多余的空格
            if "@" in line:                            #跳过测试命令那一行
                continue
            elif "rw=" in line:
                mode=line.split(",")
                data[num].append(mode[0].split("=")[2])               #获取读写模式，如randread
                i=mode[1].find("-")                                   #获得类似"bs=4M-4M/4M-4M/4M-4M"的字符串中第一个"-"的位置
                if "K" in line:
                    data[num].append(mode[1][3:i-1]+"K")              #获取读写块大小，如4K
                elif "M" in line:
                    data[num].append(mode[1][3:i-1]+"M")              #获取读写块大小，如4M
                elif "G" in line:
                    data[num].append(mode[1][3:i-1]+"G")              #获取读写块大小，如1G
                else:
                    data[num].append(mode[1][3:i]+"B")                #获取读写块大小，如512
            elif "iops=" in line:
                mode=line.split(",")
                data[num].append(int(mode[2][5:len(mode[2])]))          #获取iops，例如"iops=448"中的数字
            elif "clat(msec)" in line:
                mode=line.split(",")
                data[num].append(float(mode[2][4:len(mode[2])]))        #获取读写延迟，例如"avg=14532.06"中的数字,单位为ms
            elif "clat(usec)" in line:
                mode=line.split(",")
                data[num].append(float(mode[2][4:len(mode[2])])/1000)   #获取读写延迟，例如"avg=14532.06"中的数字，单位为us，转化为ms
            elif "bw(KB/s)" in line:                 
                mode=line.split(",")
                bw=float(mode[3][4:len(mode[3])])/1024       #获取读写吞吐率，例如"avg=2228.96,"中的数字,并将KB/s单位转化为MB/s
                data[num].append(bw)
            elif "bw(MB/s)" in line:                 
                mode=line.split(",")
                bw=float(mode[3][4:len(mode[3])])            #获取读写吞吐率
                data[num].append(bw)     
            else:                                            #跳过其他不关心的数据
                continue
    num=num+1        
    fin.close()

#将原始数据拆分到各个对应的列表，即iops，lat以及mbps（MB/s）
for dline in data:
  if "read" in dline:
    if iops[0][0]=='':
      iops[0][0]='顺序读'
    if lat[0][0]=='':
      lat[0][0]='顺序读'
    if mbps[0][0]=='':
      mbps[0][0]='顺序读'

    iops[0].append(dline[2])
    lat[0].append(dline[3])
    mbps[0].append(dline[4])
    continue
  elif "write" in dline:
    if iops[1][0]=='':
      iops[1][0]='顺序写'
    if lat[1][0]=='':
      lat[1][0]='顺序写'
    if mbps[1][0]=='':
      mbps[1][0]='顺序写'
      
    iops[1].append(dline[2])
    lat[1].append(dline[3])
    mbps[1].append(dline[4])
    continue
  elif "randread" in dline:
    if iops[2][0]=='':
      iops[2][0]='随机读'
    if lat[2][0]=='':
      lat[2][0]='随机读'
    if mbps[2][0]=='':
      mbps[2][0]='随机读'
      
    iops[2].append(dline[2])
    lat[2].append(dline[3])
    mbps[2].append(dline[4])
    continue
  else:
    if iops[3][0]=='':
      iops[3][0]='随机写'
    if lat[3][0]=='':
      lat[3][0]='随机写'
    if mbps[3][0]=='':
      mbps[3][0]='随机写'
      
    iops[3].append(dline[2])
    lat[3].append(dline[3])
    mbps[3].append(dline[4])
    continue
  

#写入iops
writer.writerow(['IOPS'])
for line in iops:
  writer.writerow(line)
writer.writerow([])

#写入读写带宽
writer.writerow(['读写带宽(MB/s)'])
for line in mbps:
  writer.writerow(line)
writer.writerow([])

#写入读写延迟带宽
writer.writerow(['读写延迟(msec)'])
for line in lat:
  writer.writerow(line)

#关闭文件 
csvfile_out.close()
end=time.time()
#输出处理结果
print "数据处理完成，耗时%fs" %(end-begin)
print "详细结果请看原始数据目录下的统计文件(与目录同名),性能峰值汇总如下：\n"
print '读写模式\t\t{0:<12}{1:<12}'.format('IOPS','读写带宽(MB/s)')
print '  顺序读\t\t{0:<12}{1:4.2f}'.format(max(iops[0][1:]),max(mbps[0][1:]))
print '  顺序写\t\t{0:<12}{1:4.2f}'.format(max(iops[1][1:]),max(mbps[1][1:]))
print '  随机读\t\t{0:<12}{1:4.2f}'.format(max(iops[2][1:]),max(mbps[2][1:]))
print '  随机写\t\t{0:<12}{1:4.2f}'.format(max(iops[3][1:]),max(mbps[3][1:]))

    
  

