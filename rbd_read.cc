#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <rados/librados.h>
#include <rbd/librbd.h>
using namespace std;

#define random(x) (rand()%x)

int main(int argc, char** argv)
{
    if ( argc < 3 )
    {
        cout <<"example: rbd_write name size:"<<endl;
        cout <<"   name: your rbd image name, e.g. myimage1"<<endl;
        cout <<"   mode: seq or rand,means sequentially or randomly read"<<endl;
        cout <<"     bk: your IO block size(KB), e.g. 4"<<endl;
        cout <<"   size: your rbd image size(MB), e.g. 512"<<endl;
        cout <<"    out: bksize,IO mode,IOPS,avg lat(ms),bw(MB/s)"<<endl;
        exit(1);
    }
    uint64_t bksize= atoi(argv[3]);
    uint64_t dsize= atoi(argv[4]);
    if (dsize <=0 )
    {
        cout <<"Error:data size must > 0 !"<<endl;
        exit(1);
    }
    if (bksize <=0 )
    {
        cout <<"Error:block size must > 0 !"<<endl;
        exit(1);
    }
    if (bksize > dsize*1024 )
    {
        cout <<"Error:block size must < data size !"<<endl;
        exit(1);
    }

    char poolname[] = "rbd";
    char *imagename=argv[1];
    size_t len=bksize*1024;
    char *data=new char[len];

    int err;
    rados_t cluster;

    err = rados_create(&cluster, NULL);
    if (err < 0)
    {
        fprintf(stderr, "%s: cannot create a cluster handle: %s\n", argv[0], strerror(-err));
        exit(1);
    }

    err = rados_conf_read_file(cluster, "/etc/ceph/ceph.conf");
    if (err < 0)
    {
        fprintf(stderr, "%s: cannot read config file: %s\n", argv[0], strerror(-err));
        exit(1);
    }
    err = rados_connect(cluster);
    if (err < 0)
    {
        fprintf(stderr, "%s: cannot connect to cluster: %s\n", argv[0], strerror(-err));
        exit(1);
    }

    rados_ioctx_t io;
    err = rados_ioctx_create(cluster, poolname, &io);
    if (err < 0)
    {
        fprintf(stderr, "%s: cannot open rados pool %s: %s\n", argv[0], poolname, strerror(-err));
        rados_shutdown(cluster);
        exit(1);
    }


    rbd_image_t pimage;
    err = rbd_open(io,imagename,&pimage,NULL);
    if (err < 0)
    {
        fprintf(stderr, "%s: cannot open rbd image pool %s(%s): %s\n", argv[0], poolname, imagename, strerror(-err));
        rados_ioctx_destroy(io);
        rados_shutdown(cluster);
        exit(1);
    }

    //计时
    struct timeval start,end;
    double tc;                       //耗时(s)
    uint64_t ofs=0;                  //偏移
    uint64_t ios=1024*dsize/bksize;  //需要写入的次数
    uint64_t i=0;                    //当前写入的次数
    bool seq=true;                   //是否顺序

    srand((int)time(0));             //随机种子
    gettimeofday(&start,NULL);       //计时开始

    if(strcmp(argv[2],"seq")==0)     //顺序操作
    {
		seq=true;
        for(i=0; i<ios; i++)
        {
            err = rbd_read(pimage,ofs,len,data);
            if (err < 0)
            {
                fprintf(stderr, "%s: cannot read rbd image pool %s(%s): %s\n", argv[0], poolname, imagename, strerror(-err));
                rados_ioctx_destroy(io);
                rados_shutdown(cluster);
                exit(1);
            }
            ofs+=len;
            //printf("Read from %s %d:\n%s\n",imagename,i++,data);
        }
    }
    else if(strcmp(argv[2],"rand")==0)  //随机操作
    {
		seq=false;
        for(i=0; i<ios; i++)
        {
            ofs=random(1024*1024*dsize); //随机偏移
            err = rbd_read(pimage,ofs,len,data);
            if (err < 0)
            {
                fprintf(stderr, "%s: cannot read rbd image pool %s(%s): %s\n", argv[0], poolname, imagename, strerror(-err));
                rados_ioctx_destroy(io);
                rados_shutdown(cluster);
                exit(1);
            }
        }
    }
    else
    {
        fprintf(stderr, "%s: %s is not a valid parameter!\n", argv[0], argv[2]);
        rados_ioctx_destroy(io);
        rados_shutdown(cluster);
        exit(1);
    }
    gettimeofday(&end,NULL);            //计时结束

    rados_ioctx_destroy(io);
    rados_shutdown(cluster);
    delete data;
    data=NULL;

    tc = end.tv_sec - start.tv_sec + (end.tv_usec - start.tv_usec)/1000000.0;
    //cout <<"run time: " <<time<<" seconds" << endl;
	if(seq)
		cout <<bksize<<"K,read,"<<(double)ios/tc<<","<<tc*1000/ios<<","<<(double)dsize/tc<<endl;
	else
		cout <<bksize<<"K,randread,"<<(double)ios/tc<<","<<tc*1000/ios<<","<<(double)dsize/tc<<endl;
    return 0;
}
