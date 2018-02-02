#!/bin/bash
#该脚本用于在安装ceph成功之后，在多个节点上搭建ceph集群
#执行时可指定存储引擎,示例如下:
#创建存储引擎为filestore的集群:./ceph-deploy.sh -f
#创建存储引擎为bluestore的集群:./ceph-deploy.sh -b
#如果不带参数,则默认为filestore存储引擎

#脚本应该在mon所在的主机上执行,因此关于mon的指令无须ssh！

#执行脚本之前的准备工作以及注意事项：
#1.在各个主机的/etc/hosts文件中加上集群中各个主机的主机名以及对应的IP，两者之间以空格隔开，例如：
#  192.168.26.147 MyCeph
#2.设置各个主机之间能够通过ssh免密登录
#3.各个osd上准备一个空闲的数据盘，脚本会重新格式化osd数据盘为ext4，还可以为日志单独设置一个日志盘
#  该日志盘可以是一个完整的磁盘，也可以是一个分区
#4.各个主机的/etc/ssh/sshd_config文件中添加配置:PermitUserEnvironment yes
#5.各个主机的/root/.ssh/文件夹下创建一个名称为environment的文件，用于设置ssh的环境变量
#  内容是：
#  PYTHONPATH=.:/usr/local/lib/python2.7/dist-packages
#  LD_LIBRARY_PATH=.:/usr/local/lib
#6.在该脚本同目录下创建一个配置文件ceph_all.conf，格式如下：
#  角色:主机名:数据盘:wal盘:db盘
#  mon:mon:
#  mds:mon:
#  OSD.0:osd0:/dev/sdb:/dev/sdc:/dev/sdd
#  OSD.1:osd2:/dev/sdc
#  OSD.2:osd3:/dev/sdd
#7.脚本执行之前确保没有其他ceph进程在运行，否则无法执行成功
#8.执行的时候需要使用./build-ceph-all.sh的方式，如果使用sh build-ceph-all.sh的方式
#  可能会出现错误，因为sh默认链接的是dash而非bash

#检查是否有配置文件
if [ ! -f "ceph_all.conf" ];then
  echo "ERROR:please edit the ceph_all.conf file!"
  exit 1
fi

#检查存储引擎参数，默认为filestore
if [ "$1" = "-b" ];then
  echo "Enable bluestore......"
  STORE=1
elif [ "$1" = "-f" ];then
  echo "Enable filestore......"
  STORE=2
elif [ "$1" = "" ];then
  echo "Enable filestore by default......"
  STORE=2
else
  echo "ERROR:must be -b or -f!"
  exit 1
fi

#脚本在mon节点上执行，获取mon的主机名和IP
MONHOST=$(hostname) 
MONIP=$(grep $MONHOST /etc/hosts |cut -d" " -f1)
UUID=$(uuidgen)
ACTION=${1-'all'}

#创建ceph配置文件
#参数:mon主机名,mon IP,UUID,存储引擎
conf_create() {
    #获取参数值
    MONHOST=${1} 
    MONIP=${2}
    UUID=${3}
	SRORE=${4}
    NET=${MONIP%.*}.0/24
    #创建集群配置文件
    echo "do some clean work..."
    #清除mon主机上残留的ceph相关数据
    if [ -d "/etc/ceph/" ];then
      echo "delete the old /etc/ceph/..."
      rm -r /etc/ceph
    fi
    mkdir -p /etc/ceph/
  
    echo "write conf file"
	touch /etc/ceph/ceph.conf
    #bluestore的集群配置文件
    if [ $SRORE == 1 ]; then
      cat >> /etc/ceph/ceph.conf <<EOF
[global]
fsid = ${UUID}
mon_initial_members = ${MONHOST}
mon_host = ${MONIP}
public_network = ${NET}
auth cluster required = cephx
auth service required = cephx
auth client required = cephx
osd pool default size = 1
osd_pool_default_pg_num = 64
osd_pool_default_pgp_num = 64
osd_crush_chooseleaf_type = 1
enable experimental unrecoverable data corrupting features = bluestore,rocksdb
osd_objectstore = bluestore
EOF
   #filestore的集群配置文件
   else
     cat >> /etc/ceph/ceph.conf <<EOF
[global]
fsid = ${UUID}
mon_initial_members = ${MONHOST}
mon_host = ${MONIP}
public_network = ${NET}
auth cluster required = cephx
auth service required = cephx
auth client required = cephx
filestore_xattr_use_omap = true
osd_journal_size = 1024
osd pool default size = 1
osd_pool_default_pg_num = 64
osd_pool_default_pgp_num = 64
osd_crush_chooseleaf_type = 1
EOF
   fi
}

#创建mon节点
#参数:主机名,IP,UUID
mon_create() {
    #获取参数值
    MONHOST=${1} 
    MONIP=${2}
    UUID=${3}
    #清除mon主机上残留的ceph相关数据
    if [ -d "/var/log/ceph/" ];then
      echo "delete the old /etc/ceph..."
      rm -r /var/log/ceph/
    fi
    mkdir -p /var/log/ceph/
  
    if [ -d "/var/lib/ceph/mon/" ];then
      echo "delete the old /var/lib/ceph/mon/..."
      rm -r /var/lib/ceph/mon/
    fi
  
    if [ -d "/var/run/ceph/" ];then
      echo "delete the old /var/run/ceph/..."
      rm -r /var/run/ceph/
    fi
  
    if [ -f "/tmp/ceph.mon.keyring" ];then
      rm /tmp/ceph.mon.keyring
    fi
  
    if [ -f "/tmp/monmap" ];then
      rm /tmp/monmap  
    fi

    #创建mon
    echo "create the mon ${MONHOST}"
    echo "create admin keyring and secret..."
    ceph-authtool --create-keyring /tmp/ceph.mon.keyring --gen-key -n mon. --cap mon 'allow *'
    echo "create client.admin and add it to ceph.client.adminkeyring..."
    ceph-authtool --create-keyring /etc/ceph/ceph.client.admin.keyring --gen-key -n client.admin --set-uid=0 --cap mon 'allow *' --cap osd 'allow *' --cap mds 'allow'
    echo "add client.admin to ceph.mon.keyring..."
    ceph-authtool /tmp/ceph.mon.keyring --import-keyring /etc/ceph/ceph.client.admin.keyring
    echo "create a monitor map..."
    monmaptool --create --add ${MONHOST} ${MONIP} --fsid ${UUID} /tmp/monmap
    echo "create mon data directory..."
    mkdir -p /var/lib/ceph/mon/ceph-${MONHOST}
    echo "create mon deamon..."
    ceph-mon --mkfs -i ${MONHOST} --monmap /tmp/monmap --keyring /tmp/ceph.mon.keyring
    #启动mon
    ceph-mon -i ${MONHOST}
}

#创建bluestore osd节点
#参数为:osd主机名,数据盘,wal盘,db盘
blue_osd_create() {
    #获取参数
    h=${1}
    data=${2}
    wal=${3}
    db=${4}
    echo "clean up obsolete data on $h"
    ssh root@$h "umount $data"
    ssh root@$h "umount $wal"
    ssh root@$h "umount $db"
    ssh root@$h "mkdir -p /etc/ceph"
    ssh root@$h "rm -r /var/log/ceph/"
    ssh root@$h "mkdir -p /var/log/ceph/"

    if [ ! -n "$data" ];then
      echo "ERROR:no bluestore block device!"
      exit 1
    fi 

    #创建osd节点
    echo "create an osd on $h"
    id=$(ceph osd create)

    #在配置文件中添加该OSD的bluestore磁盘路径
    echo "[osd.$id]" >> /etc/ceph/ceph.conf
    echo "bluestore_block_path = $data" >> /etc/ceph/ceph.conf
    #如果wal盘不为空，则在配置文件中添加配置项
    if [ -n "$wal" ];then
      echo "set wal device path..."
      echo "bluestore_block_wal_path = $wal" >> /etc/ceph/ceph.conf
      echo "bluestore_block_wal_size = 96*1024*1024" >> /etc/ceph/ceph.conf
      echo "bluestore_block_wal_create= true" >> /etc/ceph/ceph.conf
    fi
  
    #如果db盘不为空，则在配置文件中添加配置项
    if [ -n "$db" ];then
      echo "set db device path..."
      echo "bluestore_block_db_path = $db" >> /etc/ceph/ceph.conf
      echo "bluestore_block_db_size = 1024*1024*1024" >> /etc/ceph/ceph.conf
      echo "bluestore_block_db_create= true" >> /etc/ceph/ceph.conf
    fi

    #拷贝集群的配置文件到osd主机上的对应目录下
    if [ $(hostname) != $h ];then 
      scp /etc/ceph/* $h:/etc/ceph
    fi
  
    #删除osd上的旧数据
    ssh root@$h "rm -r /var/lib/ceph/osd/ceph-$id/"
    #创建osd 
    echo "create $role data directory..."
    ssh root@$h "mkdir -p /var/lib/ceph/osd/ceph-$id"
    echo "init $role data directory..."
    ssh root@$h "ceph-osd -i $id --mkfs --mkkey"
    echo "create auth key..."
    ssh root@$h "ceph auth add osd.$id osd 'allow *' mon 'allow profile osd' -i /var/lib/ceph/osd/ceph-$id/keyring"
    echo "add $role to crush map..."
    ceph osd crush add-bucket OSD$id host
    ceph osd crush move OSD$id root=default
    ceph osd crush add osd.$id 1.0 host=OSD$id
    echo "start osd $id"
    ceph-osd -i $id
    #在/etc/fstab中添加挂载项
    echo "add osd devices to /etc/fstab"
    ssh root@$h "cp /etc/fstab /etc/fstab.bak"
    rmd=${data:5:9} #获取数据盘名称，例如sdb,sdc
    #删除旧的osd数据盘条目
    ssh root@$h "sed -i '"/$rmd/d"' /etc/fstab" 
}

#创建filestore osd节点
#参数为:osd主机名,数据盘,日志盘
file_osd_create() {
    #获取参数
    h=${1}
    data=${2}
    wal=${3} 
    echo "do some clean work on $h..."
    ssh root@$h "umount $data"
    ssh root@$h "mkdir -p /etc/ceph"
    ssh root@$h "rm -r /var/log/ceph/"
    ssh root@$h "mkdir -p /var/log/ceph/"
  
    #拷贝集群的配置文件到osd主机上的对应目录下
    if [ $(hostname) != $h ];then 
      scp /etc/ceph/* $h:/etc/ceph
    fi
  
    id=$(ceph osd create)
    #删除osd上的旧数据
    ssh root@$h "rm -r /var/lib/ceph/osd/ceph-$id/"
    #创建osd 
    echo "create $role data directory..."
    ssh root@$h "mkdir -p /var/lib/ceph/osd/ceph-$id"
    echo "format $role data device..."
    ssh root@$h "mkfs.ext4 -F $data"
    echo "mount $role data device..."
    ssh root@$h "mount -o user_xattr $data /var/lib/ceph/osd/ceph-$id/"
    echo "init $role data directory..."
    ssh root@$h "ceph-osd -i $id --mkfs --mkkey"
    echo "create auth key..."
    ssh root@$h "ceph auth add osd.$id osd 'allow *' mon 'allow profile osd' -i /var/lib/ceph/osd/ceph-$id/keyring"
    echo "add $role to crush map..."
    ceph osd crush add-bucket OSD$id host
    ceph osd crush move OSD$id root=default
    ceph osd crush add osd.$id 1.0 host=OSD$id
    
    #如果设置了日志盘，则需要在配置文件中添加
    if [ $wal ];then
      echo "[osd.$id]" >> /etc/ceph/ceph.conf
      echo "osd journal = $wal" >> /etc/ceph/ceph.conf
      echo "osd_journal_size = 0" >> /etc/ceph/ceph.conf
      #激活日志盘
      ssh root@$h "ceph-osd --mkjournal -i $id"
    fi
    #启动osd
    ssh root@$h "ceph-osd -i $id"

    #在/etc/fstab中添加挂载项
    echo "add osd devices to /etc/fstab"
    ssh root@$h "cp /etc/fstab /etc/fstab.bak"
    rmd=${data:5:9} #获取数据盘名称，例如sdb,sdc
    #删除旧的osd数据盘条目
    ssh root@$h "sed -i '"/$rmd/d"' /etc/fstab" 
    #添加新的挂载选项
    ssh root@$h "echo '"$data /var/lib/ceph/osd/ceph-$id ext4 defaults 0 0"' >> /etc/fstab"
}

#创建mds节点
#参数:mds主机名
mds_create() {
    h=${1}
    echo "create a single mds on $h"
    #清理mds节点上的残留ceph数据
    echo "do some clean work on $h..."
	ssh root@$h "rm -r /var/lib/ceph/mds/*"
	ssh root@$h "rm -r /var/log/ceph"
    ssh root@$h "mkdir -p /var/log/ceph/"
    ssh root@$h "mkdir -p /etc/ceph"
    
    if [ $(hostname) != $h ];then 
      scp /etc/ceph/* $h:/etc/ceph
    fi
   
    echo "create mds..."
    echo "create mds data directory..."
    ssh root@$h "mkdir -p /var/lib/ceph/mds/ceph-$h/"
    
    echo "create mds key..."
    ssh root@$h "ceph auth get-or-create mds.$h mds 'allow ' osd 'allow *' mon 'allow rwx' > /var/lib/ceph/mds/ceph-$h/keyring"
    
    echo "start mds..."
    ssh root@$h "ceph-mds -i $h"
}

#根据ceph_all.conf文件配置各个节点
for p in $(cat ceph_all.conf)
do
  role=$(echo $p |cut -d":" -f1)          #获取角色名
  h=$(echo $p |cut -d":" -f2)             #获取主机名
  data=$(echo $p |cut -d":" -f3)          #获取数据盘路径
  wal=$(echo $p |cut -d":" -f4)           #获取bluestore的wal盘,或者filestore的journal盘
  db=$(echo $p |cut -d":" -f5)            #获取ibluestore的db盘路径
  ip=$(grep $h /etc/hosts |cut -d" " -f1) #获取IP
  #根据不同的角色进行不同的操作
  case $role in
  "mon") #mon上的操作
  echo "#######Create /etc/ceph/ceph.conf*****************************************************************************"
  conf_create $MONHOST $MONIP $UUID $STORE
  echo "#######Create MON*********************************************************************************************"
  mon_create $MONHOST $MONIP $UUID
  ;;
  "mds") #mds上的操作
  echo "#######Create MDS*********************************************************************************************"
  mds_create $h
  ;;
  "OSD."*) #osd上的操作
  echo "#######Create OSD*********************************************************************************************"
  if [ "$STORE" = "1" ];then
    blue_osd_create $h $data $wal $db 
  else
    file_osd_create $h $data $wal
  fi
  ;;
  "#"*)
  ;;
  *)
  echo "$role:ceph_hosts role name error!"
  exit 1
  ;;
esac
done    


#将新的配置文件拷贝到此mon节点之外的其他节点上
for p in $(cat ceph_all.conf)
do
  h=$(echo $p |cut -d":" -f2)     #获取主机名
  #只有目标主机不是当前主机时才发送
  if [ $(hostname) != $h ];then
    scp /etc/ceph/ceph.conf $h:/etc/ceph
  else
    continue
  fi
done

echo "#######Create filesystem*****************************************************************************************"
echo "create filesystem pool..."
ceph osd pool create cephfs_data 64
ceph osd pool create cephfs_metadata 64

echo "create a new filesystem..."
ceph fs new cephfs cephfs_metadata cephfs_data

echo "#######Done!*****************************************************************************************************"
echo "++++++++++++++ceph status:++++++++++++++"
ceph -s
ceph osd tree

