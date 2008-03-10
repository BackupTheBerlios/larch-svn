// lodtch.c
// A utility to detach loop devices for klibc environment
// To compile:
// klcc -static -o lodtch lodtch.c

/* Adapted from 'mount/lomount.c', function 'del_loop' in util-linux-ng-2.13.0.1 */

#include <stdio.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <string.h>
#include <linux/loop.h>

int main(int argc, const char ** argv)
{
    int fd = -1;

    if (argc != 2)
    {
        fprintf(stderr, "Usage: lodtch <loop device>\n");
        return 1;
    }

    if ((fd = open (argv[1], O_RDONLY)) < 0)
    {
        int errsv = errno;
        fprintf(stderr, "loop: can't delete device %s: %s\n",
            argv[1], strerror (errsv));
        return 1;
    }

    if (ioctl (fd, LOOP_CLR_FD, 0) < 0)
    {
        perror ("ioctl: LOOP_CLR_FD");
        close(fd);
        return 1;
    }
    close (fd);
    return 0;
}
