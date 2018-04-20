#include <iostream>
#include <fstream>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <error.h>
#include <random>
#include <sys/stat.h>

using namespace std;


int main(int argc, char** argv)
{
    if (argc < 5)
    {
        cout <<"example: trace_gen trace_name data_size type:"<<endl;
        cout <<" trace_name: your trace name, e.g., trace1"<<endl;
        cout <<"circle_size: your trace data size for every circle in GB, e.g., 4"<<endl;
        cout <<"       type: ran(random) or seq(sequential), seq by default"<<endl;
        cout <<"     circle: num of circles"<<endl;
        exit(1);
    }

    //time record
	struct timespec start,end;
    double tc;                        //time consumed
    uint32_t circle=0;

	default_random_engine random(time(NULL));

	//get arguments from command
	uint32_t blk_size = 4096; //block size is 4K
    const char *trace_name = argv[1]; 
    uint64_t nr_blocks=atol(argv[2])*1024*1024*1024/blk_size; //block number

	uniform_int_distribution<uint64_t> random_uint(0, nr_blocks);

	int seq = 1;
	if ((argv[3] == "random") || (argv[3] == "ran"))
		seq = 0;
	else
		seq = 1;

    circle = atoi(argv[4]);
    uint64_t lbn=0;
    uint64_t count=0;
    uint64_t max_lbn=0;

	//file operations
	ofstream fout;
	fout.open(trace_name, std::ios::binary);
	clock_gettime(CLOCK_MONOTONIC_RAW, &start);//begin timing
	for (int i=0; i<circle; i++)
	{
		lbn=0;
		for(count=0; count<=nr_blocks; count++)
		{
			fout.write((char *)(&lbn),4);
			cout <<lbn<<endl;
			if(lbn > max_lbn)
				max_lbn = lbn;
			if(seq)
				lbn++;
			else 
				lbn = random_uint(random);
		}
	}
	max_lbn ++;
	fout.write((char *)(&max_lbn),4);

	double disk_size = blk_size*max_lbn/1024/1024/1024; //disk size in GB
	double data_size = circle*blk_size*nr_blocks/1024/1024/1024; //data size in GB

	clock_gettime(CLOCK_MONOTONIC_RAW, &end);//end timing
    tc = end.tv_sec - start.tv_sec + (end.tv_nsec - start.tv_nsec)/1000000000.0;

	//close files
	fout.close();

	//out format:
	//trace_name, lbn count, max lbn, disk_size(GB), data_size(GB), stat time elapse(s)
	cout<<trace_name<<", "<<nr_blocks<<", "<<max_lbn<<", "
		<<disk_size<<", "<<data_size<<", "<<tc<<endl;

    return 0;
}
