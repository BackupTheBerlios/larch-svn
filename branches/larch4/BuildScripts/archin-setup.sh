#!/bin/sh

echo
echo "This script fetches and unpacks pacin and archin, so that 'archin' can"
echo "be run from this directory, without installing."
echo "It also generates a convenient symlink to the 'archin' script."
echo

REPO="ftp://archie.dotsrc.org/projects/archie/larch/testing"
#REPO="http://www.faunos.com/larch/testing"
#REPO="file:///home/larch/testing"

# Get path to this directory, via the location of this script
fullpath="$( readlink -f $0 )"
scriptdir="$( dirname ${fullpath} )"

# Just in case ...
cd ${scriptdir}

fetch ()
{
    if [ -n "$( echo ${REPO} | grep "file://" )" ]; then
    base="$( echo ${REPO} | sed "s|file://||" )"
    cp ${base}/$1 .
    else
    wget ${REPO}/$1
    fi
}

rm -rf tmp
mkdir tmp
cd tmp
fetch larch.db.tar.gz
tar -xzf larch.db.tar.gz
d=$( ls | grep "^pacin-" )
pacinpak=$( grep -A 1 -e "%FILENAME%" ${d}/desc | grep -v "%" )
d=$( ls | grep "^archin-" )
archinpak=$( grep -A 1 -e "%FILENAME%" ${d}/desc | grep -v "%" )
cd ..

rm -rf tmp
mkdir tmp
cd tmp
fetch ${pacinpak}
fetch ${archinpak}
tar -xzf ${pacinpak}
tar -xzf ${archinpak}
cd ${scriptdir}
path=$( find tmp -name archin -type f )
root=$( dirname $( dirname ${path} ) )
rm -rf archindir
cp -a ${root} archindir
rm -rf tmp

ln -sf ${scriptdir}/archindir/bin/archin archin
