/*
 * version of copy command using async i/o
 * From:	Stephen Hemminger <shemminger@osdl.org>
 * Modified by Wang Haitao to replay disk IO trace file.
 *	   -a: alignment
 *	   -b: blksize 
 *	   -n: num of io submitted one time, i.e., io queue size
 *	   -w: write option (1 for write, 0 default)
 *	   -D: delay_ms option
 *	   -s: target device size
 *	   -t: replay time in seconds, 300 default
 *	   -r: replay rounds, 2 default, i.e., replay the trace 2 times
 * device: target device
 *	trace: trace file
 *
 * Usage: replay [-a align] [-b blksize] [-n num_aio] [-w write] [-s dev_size] [-t seconds] [-r rounds] device trace
 */

#include <unistd.h>
#include <stdio.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/param.h>
#include <fcntl.h>
#include <errno.h>
#include <stdlib.h>
#include <mntent.h>
#include <sys/select.h>
#include <sys/stat.h>
#include <time.h>
#include <libaio.h>
#include <iostream>
#include <fstream>
using namespace std;

#define AIO_BLKSIZE	(64*1024)
#define AIO_MAXIO	32
#define random(x) (rand()%x)

static int aio_blksize = AIO_BLKSIZE;
static int aio_maxio = AIO_MAXIO;
static int devfd;		    // device fd
static int tracefd;		    // trace fd
static int debug = 0;       // debug option, 1 for debug
static int is_write = 0;    // is write or not, read default
static int count_io_q_waits;// how many time io_queue_wait called
static int dev_open_flag = O_RDONLY|O_DIRECT;	//open flags on dev

static uint64_t busy = 0;	    // # of I/O's in flight
static uint64_t nr_io = 0;	    // # of blocks left to read or write
static uint64_t nr_done = 0;    // # of blocks done
static uint64_t dev_size = 0;   // target device size
static uint32_t run_time = 0;   // run time of replay, 0 means no timeout
static uint32_t round = 2;      // how many rounds to replay the trace

struct iocb **iocb_free;    	// array of pointers to iocb
int iocb_free_count;	    	// current free count
int alignment = 512;	    	// buffer alignment
struct timeval delay;	    	// delay between i/o

static const char *trace_name = NULL;
static const char *dev_name = NULL;

/*
 * get a random string
 * len: the string length
*/
string random_string(int len)
{
    string ret;
    string alphanum = "0123456789"
                      "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                      "abcdefghijklmnopqrstuvwxyz";
    for (int i = 0; i < len; ++i)
    {
        ret.push_back(alphanum[rand() % (alphanum.size() - 1)]);
    }
    return ret;
}

/* get file size */
uint64_t get_file_size(const char* filename)
{
    struct stat statbuf;
    stat(filename,&statbuf);
    uint64_t size=statbuf.st_size;

    return size;
}

/* initialize the io callback struct */
int init_iocb(int n, int iosize)
{
    void *buf;
    int i;

    if ((iocb_free = (struct iocb**)malloc(n * sizeof(struct iocb *))) == 0)
    {
        return -1;
    }

    for (i = 0; i < n; i++)
    {
        if (!(iocb_free[i] = (struct iocb*)malloc(sizeof(struct iocb))))
            return -1;
        if (posix_memalign(&buf, alignment, iosize))
            return -1;
        if (debug)
        {
            printf("buf allocated at 0x%p, align:%d\n", buf, alignment);
        }
		if ( is_write)
			io_prep_pwrite(iocb_free[i], -1, buf, iosize, 0);
		else 
			io_prep_pread(iocb_free[i], -1, buf, iosize, 0);
    }
    iocb_free_count = i;
    return 0;
}

/* allocate a io callback struct */
static struct iocb *alloc_iocb(void)
{
    if (!iocb_free_count)
        return 0;
    return iocb_free[--iocb_free_count];
}

/* free a io callback struct */
void free_iocb(struct iocb *io)
{
    iocb_free[iocb_free_count++] = io;
}

/* io_wait_run() - wait for an io_event and then call the callback */
int io_wait_run(io_context_t ctx, struct timespec *to)
{
    struct io_event events[aio_maxio];
    struct io_event *ep;
    int ret, n;

    /* get up to aio_maxio events at a time */
    ret = n = io_getevents(ctx, 1, aio_maxio, events, to);

    /* Call the callback functions for each event */
    for (ep = events; n-- > 0; ep++)
    {
        io_callback_t cb = (io_callback_t) ep->data;
        struct iocb *iocb = ep->obj;

        if (debug)
        {
            fprintf(stderr, "ev:%p iocb:%p res:%ld res2:%ld\n", ep, iocb, ep->res, ep->res2);
        }
        cb(ctx, iocb, ep->res, ep->res2);
    }
    return ret;
}

/* Fatal error handler */
static void io_error(const char *func, int rc)
{
    if (rc == -ENOSYS)
        fprintf(stderr, "AIO not in this kernel\n");
    else if (rc < 0)
        fprintf(stderr, "%s: %s\n", func, strerror(-rc));
    else
        fprintf(stderr, "%s: error %d\n", func, rc);

    exit(1);
}

/*
 * Write complete callback.
 * Adjust counts and free resources
 */
static void wr_done(io_context_t ctx, struct iocb *iocb, long res, long res2)
{
    if (res2 != 0)
    {
        io_error("aio write", res2);
    }
    if (res != iocb->u.c.nbytes)
    {
        fprintf(stderr, "write missed bytes expect %lu got %ld\n", iocb->u.c.nbytes, res);
        exit(1);
    }
    if (nr_io > 0)
        --nr_io;
    if (busy > 0)
        --busy;
	nr_done ++;
    free_iocb(iocb);
}

/*
 * Read complete callback.
 * Change read iocb into a write iocb and start it.
 */
static void rd_done(io_context_t ctx, struct iocb *iocb, long res, long res2)
{
    /* library needs accessors to look at iocb? */
    int iosize = iocb->u.c.nbytes;
    char *buf = (char *)iocb->u.c.buf;
    off_t offset = iocb->u.c.offset;

    if (res2 != 0)
        io_error("aio read", res2);
    if (res != iosize)
    {
        fprintf(stderr, "read missing bytes expect %lu got %ld\n",
                iocb->u.c.nbytes, res);
        exit(1);
    }
    if (nr_io > 0)
        --nr_io;
    if (busy > 0)
        --busy;
	nr_done ++;
    free_iocb(iocb);
}

static void usage(void)
{
    cerr<<"Usage: replay [-a align] [-b blksize] [-n num_io] [-s dev_size] [-t seconds] [-r rounds] dev_name trace_name"<<endl;
    exit(1);
}

/* Scale value by kilo, mega, or giga */
long long scale_by_kmg(long long value, char scale)
{
    switch (scale)
    {
    case 'g':
    case 'G':
        value *= 1024;
    case 'm':
    case 'M':
        value *= 1024;
    case 'k':
    case 'K':
        value *= 1024;
        break;
    case '\0':
        break;
    default:
        usage();
        break;
    }
    return value;
}

int main(int argc, char *const *argv)
{
    int c;
    struct stat st;
    off_t length = 0, offset = 0;
    extern char *optarg;
    extern int optind, opterr, optopt;
    io_context_t myctx;

    while ((c = getopt(argc, argv, "a:b:d:n:s:t:r:wD:")) != -1)
    {
        char *endp;

        switch (c)
        {
        case 'a':	// alignment of data buffer
            alignment = strtol(optarg, &endp, 0);
            alignment = (long)scale_by_kmg((long long)alignment,*endp);
            break;
        case 'D':
            delay.tv_usec = atoi(optarg);
            break;
        case 'b':	// block size
            aio_blksize = strtol(optarg, &endp, 0);
            aio_blksize = (long)scale_by_kmg((long long)aio_blksize, *endp);
            break;
        case 'n':	// num io
            aio_maxio = strtol(optarg, &endp, 0);
            break;
        case 's':	// dev size
            dev_size = strtol(optarg, &endp, 0);
            dev_size = (long)scale_by_kmg((long long)aio_blksize, *endp);
            break;
        case 't':
            run_time = atoi(optarg);
            break;
        case 'r':
            round = atoi(optarg);
            break;
        case 'w':
            is_write = 1;
            break;
        default:
            usage();
        }
    }

    if (!dev_size)
        usage();

    argc -= optind;
    argv += optind;
    if (argc < 1)
    {
        usage();
    }

    // open target device
    if ((devfd = open(dev_name = *argv, dev_open_flag)) < 0)
    {
        perror(dev_name);
        exit(1);
    }
    if (fstat(devfd, &st) < 0)
    {
        perror("fstat");
        exit(1);
    }
    if (length == 0)
        length = st.st_size;

    argv++;
    argc--;
    if (argc < 1)
    {
        usage();
    }
    trace_name = *argv;

    //time record
    struct timespec start,end;
    double tc;                        //time consumed

	int rc = 0;                       //return value of io operation
    uint32_t lbn;                     //lbn from trace
    uint32_t max_lbn=0;               //max lbn number from trace
    uint64_t ofs=0;                   //offset on the disk
    double disk_size=0.0;             //disk size we need(GB)
    double data_size=0.0;             //io data size(GB)

    uint64_t max_dev_lbn = dev_size/aio_blksize;
    uint64_t fsize = get_file_size(trace_name);
    uint64_t num = fsize/4-1;
    data_size=num*aio_blksize/1024/1024/1024;

    //file operations
    ifstream fin;
    fin.open(trace_name, std::ios::binary);
    //the last 4B data is max_lbn in trace
    fin.seekg(-4,fin.end);
    fin.read((char *)(&max_lbn),4);
    disk_size = max_lbn*aio_blksize/1024/1024/1024;

    /* initialize io state machine */
    memset(&myctx, 0, sizeof(myctx));
    io_queue_init(aio_maxio, &myctx);

    if (init_iocb(aio_maxio, aio_blksize) < 0)
    {
        cerr<<"Error allocating the i/o buffers"<<endl;
        exit(1);
    }

    clock_gettime(CLOCK_MONOTONIC_RAW, &start);//begin timing
    for (int ir=0; ir<round; ir++)
    {
        nr_io = num;
		//return to the begin of file
		fin.seekg(0);
        cout<<"total round = "<<round<<", current round = "<<ir<<endl;

		clock_gettime(CLOCK_MONOTONIC_RAW, &end);//end timing
		if (run_time && ((end.tv_sec - start.tv_sec) >= run_time))
			break;
        while (nr_io > 0)
        {
            // submit as many ios as once as possible up to aio_maxio
            int n = MIN(MIN(aio_maxio - busy, aio_maxio),nr_io);
            if (n > 0)
            {
                struct iocb *ioq[n];

                for (int i = 0; i < n; i++)
                {
                    // read lbn from trace file
                    fin.read((char *)(&lbn),4);
                    // lbn need to be smaller than dev size
                    lbn = lbn%max_dev_lbn;
                    //cout<<"lbn="<<lbn<<", max_dev_lbn="<<max_dev_lbn<<endl;
                    struct iocb *io = alloc_iocb();
                    offset = lbn*aio_blksize;
					// prepare io struct and set callbak
                    if (is_write)
                    {
                        io_prep_pwrite(io, devfd, io->u.c.buf, aio_blksize, offset);
                        io_set_callback(io, wr_done);
                    }
                    else
                    {
                        io_prep_pread(io, devfd, io->u.c.buf, aio_blksize, offset);
                        io_set_callback(io, rd_done);
                    }
                    ioq[i] = io;
                }

				// submit n ios
                rc = io_submit(myctx, n, ioq);
                if (rc < 0)
                    io_error("io_submit", rc);
                busy += n;

                if (debug)
                    printf("io_submit(%d) busy:%d\n", n, busy);
				// delay a few seconds between ios if set
                if (delay.tv_usec)
                {
                    struct timeval t = delay;
                    (void)select(0, 0, 0, 0, &t);
                }
            }

            /*
             * We have submitted all the i/o requests. Wait for at least one to complete
             * and call the callbacks.
             */
            count_io_q_waits++;
            rc = io_wait_run(myctx, 0);
            if (rc < 0)
                io_error("io_wait_run", rc);

            if(debug)
            {
                printf("io_wait_run: rc == %d\n", rc);
                printf("busy:%d aio_maxio:%d nr_io:%d\n", busy, aio_maxio, nr_io);
            }
        }
    }
    clock_gettime(CLOCK_MONOTONIC_RAW, &end);//end timing
    tc = end.tv_sec - start.tv_sec + (end.tv_nsec - start.tv_nsec)/1000000000.0;

    uint64_t ios = nr_done;           // the number of ios actually done
    uint64_t iops = ios/tc;           // IOPS
    double bw = 1.0*iops*aio_blksize/1024/1024; //MB/s

    //out format:
    //trace_name, device, data_size(GB), time_elapse(s), iops, bw(MB/s)
    cout<<trace_name<<", "<<dev_name<<", IO data size(GB)="<<1.0*ios*aio_blksize/1024/1024/1024
        <<", time(s)="<<tc<<", iops="<<iops<<", BW(MB/s)="<<bw<<endl;

    if (devfd != -1)
        close(devfd);

    return 0;
}
