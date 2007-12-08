// A C version of rc.shutdown2?
// To compile:
// klcc -static -o sd2 sd2.c

#include <unistd.h>
#include <sys/mount.h>
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char *argv[])
{
  char word[256] = "/";
  char *r = NULL;
  FILE *file = fopen("/.livesys/unions", "r");

  do {
    r = fgets(word+1, 250, file);
// With fgets the strings (probably) have '\n' at the end

    if (r) {

      // remove possible '\n'
      char *strend = index(word, 10);
      if (strend) *strend = 0;

      printf("Unmounting %s\n", word);

      if (umount2(word, 0) == -1) {
        perror("umount2");
        return 255;
      }

    }
  } while (r);

  fclose(file);

  printf("Unmount sqfs\n");

  system("umount -n -d /.livesys/home && umount -n -d /.livesys/overlay && "
        "umount -n -d /.livesys/system");

  if ( execl("rc.shutdown3", "rc.shutdown3", argv[1], argv[2], (char *) NULL) == -1) {
    printf("execl failed\n");
    return 255;
  }
}

// To compile?
// klcc -static -o sd2 sd2.c

/*
--------------------------------------------
sh version:

#!/.livesys/larch-static-bin/sh_static
# 2007.11.07

# Unmount the union mounts, so that the cd can be written to or ejected
# During the unmounting, the file systems being unmounted should not be
# in use, so use statically linked shell and unmount utility.

echo "Returning to minimal 'base' system"
for d in $( cat /.livesys/unions ); do
    /.livesys/larch-static-bin/umount_static /${d}
done
umount -n -d /.livesys/home
umount -n -d /.livesys/overlay
umount -n -d /.livesys/system


-- cut here? --


umount -n /.livesys/livecd 2>/dev/null
umount -n /.livesys/savedev 2>/dev/null
if [ -f /.livesys/scripts/shutdown-unmount ]; then
    . /.livesys/scripts/shutdown-unmount
fi
exec /etc/rc.shutdown3 "$1" "$2"
*/
