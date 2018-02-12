#include <iostream>
#include <fstream>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <error.h>
#include <sys/stat.h>

using namespace std;


/* get file size */
uint64_t file_size(const char* filename)  
{  
    struct stat statbuf;  
    stat(filename,&statbuf);  
    uint64_t size=statbuf.st_size;  
  
    return size;  
}

int main(int argc, char** argv)
{
    if (argc < 2)
    {
        cout <<"example: trace_stat trace_name debug:"<<endl;
        cout <<"trace_name: your trace name, e.g., trace1"<<endl;
        cout <<"      dump: if 1, then dump lbn to output. 0 by default"<<endl;
        cout <<"       out: trace_name, lbn count, max lbn, disk_size(GB), data_size(GB), stat time elapse(s)"<<endl;
        exit(1);
    }
	int dump = 0;

    //time record
	struct timespec start,end;
    double tc;                        //time consumed

	//get arguments from command
	const uint32_t io_size = 4096;     //IO size is 4K
    const char *trace_name = argv[1]; 

	if (argv[2])
		dump = atoi(argv[2]);

    uint32_t count=0;
	uint32_t lbn;
    uint32_t max_lbn=0;               //max lbn number
    uint64_t ofs=0;                   //offset on the disk
    double disk_size=0.0;             //disk size we need(GB)
    double data_size=0.0;             //io data size(GB)

	uint64_t fsize = file_size(trace_name);
	uint64_t num = fsize/4-1;
    data_size=1.0*num*io_size/1024/1024/1024;

	//file operations
	ifstream fin;
	fin.open(trace_name, std::ios::binary);
	//the last 4B data is max_lbn in trace
	fin.seekg(-4,fin.end);
	fin.read((char *)(&max_lbn),4);
	disk_size = 1.0*max_lbn*io_size/1024/1024/1024;
	//return to the begin of file
	fin.seekg(0);

	clock_gettime(CLOCK_MONOTONIC_RAW, &start);//begin timing
	for(int i=0; i<num; i++)
	{
		fin.read((char *)(&lbn),4);
		if(dump)
			cout<<lbn<<endl;
	}

	clock_gettime(CLOCK_MONOTONIC_RAW, &end);//end timing
    tc = end.tv_sec - start.tv_sec + (end.tv_nsec - start.tv_nsec)/1000000000.0;

	//close files
	fin.close();

	//out format:
	//trace_name, lbn count, max lbn, disk_size(GB), data_size(GB), stat time elapse(s)
	cout<<trace_name<<", "<<num<<", "<<max_lbn<<", "
		<<disk_size<<", "<<data_size<<", "<<tc<<endl;

    return 0;
}
