// rename.c
// A rename utility for klibc environment
// To compile:
// klcc -static -o rename rename.c

#include <stdio.h>

int main(int argc, char *argv[])
{
  if ( argc != 3 ) return 1;
  return rename(argv[1], argv[2]);
}

