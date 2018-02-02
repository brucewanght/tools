# coding: utf-8
#coding=utf-8
#该程序用于提取出iometer测试结果文件中的IOPS，吞吐率，平均响应时间以及CPU利用率
#注意：使用该程序的时候，测试的原始数据需要保存为指定格式，即“iometer-测试名称”
#例如"iometer-ceph块设备读.csv"
#处理后的结果保存在"pro-文件名.csv"中，例如上述数据文件处理完成之后就会保存为
#pro-iometer-ceph块设备读.csv
import csv
import os

flist=[]
filenames=os.listdir(os.getcwd())
for fn in filenames:
  if "iometer-" in fn:
     flist.append(fn)

for fn in flist:
    csvfile_in = file(fn, 'rb')
    csvfile_out = file("Pro-"+fn, 'wb')
    reader = csv.reader(csvfile_in)
    writer = csv.writer(csvfile_out)
    writer.writerow(['读写模式','IOPS','吞吐率(MB/s)','平均响应时间(ms)','CPU利用率(%)'])
    for line in reader:
        if 'ALL' in line:
            data=[line[2],line[6],line[9],line[17],line[48]]
            writer.writerow(data)
    csvfile_in.close()
    csvfile_out.close()
