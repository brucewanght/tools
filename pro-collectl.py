#coding=utf-8
#注意：使用该程序的时候，测试的原始数据需要保存为指定格式，即“机器名-t测试编号”
#例如第一次测试，对于mon主机的原始数据则应保存为“mon-t1”,处理之后，会将处理后
#的结果输出到一个csv文件中，每个原始数据文件对应一个csv，csv的名称则是在原始
#数据文件名前面加“Pro-”，例如原始文件为“mon-t1”则处理后的数据对应保存为“Pro-mon-t1.csv”

#需要处理的数据与该程序要放在同一目录下

#负载均衡测试的原始数据使用Collectl工具采集(Collectl -scdmn)，原始数据格式如下：
'''
waiting for 1 second sample...
#<--------CPU--------><-----------Memory-----------><----------Disks-----------><----------Network---------->
#cpu sys inter  ctxsw Free Buff Cach Inac Slab  Map KBRead  Reads KBWrit Writes   KBIn  PktIn  KBOut  PktOut 
  56  24 69911 153028  12G 150M   1G   1G  88M   1G      0      0      4      1   5921  24033   8060   24183 
  55  23 62327 142095  12G 150M   1G   1G  88M   1G      0      0   2108     64   7693  23840   7906   23515 
  60  25 56748 166301  12G 150M   1G   1G  88M   1G      4      1   2836     83   8616  27197   8141   25981 
  59  24 75259 139999  13G 150M   1G   1G  87M   1G     64     16   7152     95   4860  21984   6074   21939 
  56  22 64077 119882  13G 151M   1G 872M  87M   1G     60     15   2736    153   5199  18510   5596   18200 
  60  24 56109 135307  13G 151M 715M 558M  86M   1G    100     25   2248    140   6191  20911   6556   21093 
  57  23 62800 144837  13G 151M 532M 393M  85M   1G     76     19    520     73   4656  20782   6519   21162 
  59  25 73153 160353  13G 151M 532M 393M  85M   1G      0      0      0      0   3611  23671   5741   23436 
  51  22 78814 127236  13G 151M 532M 393M  85M   1G      0      0    104      6   3407  19529   5162   19283 
  54  23 74653 142500  13G 151M 529M 390M  85M   1G      0      0   4496     54   3729  21180   5626   20839 
  49  21 74689 128048  13G 151M 529M 390M  85M   1G      0      0    136     10   2904  18783   4659   18432 
  53  22 66993 143587  13G 151M 529M 390M  84M   1G      0      0     88      6   4744  21263   6782   21680 
  61  25 55546 181520  13G 151M 529M 390M  85M   1G      0      0      0      0   4348  25604   6697   25565 
  55  23 60920 156230  13G 151M 529M 390M  85M   1G      0      0     56      6   4147  22639   6240   22648 
  56  23 54617 158614  13G 151M 529M 391M  85M   1G      0      0   1244     39   5796  23450   6896   23405 
  58  24 57041 161353  13G 151M 527M 391M  84M   1G      0      0   3420     72   7321  23944   7398   23768 
  58  24 61577 161976  13G 151M 528M 392M  84M   1G      0      0   1224     34   5826  23972   6893   23674 
  58  25 71801 154915  13G 151M 528M 392M  84M   1G      0      0      0      0   3601  23686   5702   23191 
  51  22 66735 134326  13G 151M 528M 392M  84M   1G      0      0     56      6   3413  19610   5210   19416 
  51  22 63057 141534  13G 151M 524M 389M  84M   1G      0      0   4452     45   3521  20452   5413   20250 
  62  27 57056 179508  13G 151M 524M 388M  84M   1G      0      0      0      0   3849  26867   6167   26281 
  57  25 69966 158710  13G 151M 524M 388M  84M   1G      0      0      0      0   4078  23475   6156   23192 
#<--------CPU--------><-----------Memory-----------><----------Disks-----------><----------Network---------->
#cpu sys inter  ctxsw Free Buff Cach Inac Slab  Map KBRead  Reads KBWrit Writes   KBIn  PktIn  KBOut  PktOut 
  58  25 70808 161672  13G 151M 524M 388M  84M   1G      0      0      0      0   3721  23654   5819   23256 
  55  23 65911 149885  13G 151M 524M 388M  84M   1G      0      0     40      6   4328  22545   6432   22698 
'''
import csv
import os

flist=[]
filenames=os.listdir(os.getcwd())

for fn in filenames:
  if "-t" in fn:
     flist.append(fn)
     
for fn in flist:
    csvfile_out = file("Pro-"+fn+'.csv', 'wb')         #创建输出处理后数据的csv文件
    writer = csv.writer(csvfile_out)                   #创建用于输出数据的writer
    writer.writerow(['%CPU','Cach(MB)','RW IO/s','RW MB/s','NetIO MB/s'])
    with open(fn, "r") as fin:
        for line in fin:
            if line.startswith('waiting for'):         #跳过文件开头的提示信息
                continue
            elif line.startswith('#'):                 #跳过表头
                continue
            elif line.startswith(' '):                 #实际的测试数据是以空格开头的，其余的都不是数据
                line.strip();
                nums = line.split()                    #按空白切分行，得到一组数值
                if len(nums)==18:                      #只计算数据完整的行
                    data=[]                            #创建用于保存处理后数据的列表
                    data.append(nums[0])
                    if "G" in nums[6]:                 #去掉cache数据最后的字符G，并乘以1024将其换为以M为单位的数据
                        data.append(int(nums[6][0:len(nums[6])-1])*1024)
                    else:
                        data.append(int(nums[6][0:len(nums[6])-1]))
                    data.append(int(nums[11])+int(nums[13]))                #读写IO/s
                    data.append(float(nums[10])/1024+float(nums[12])/1024)  #硬盘读写速率，单位为MB/s
                    data.append(float(nums[14])/1024+float(nums[16])/1024)  #网络读写速率，单位为MB/s
                    writer.writerow(data)
                else:
                    break
fin.close()
csvfile_out.close()
