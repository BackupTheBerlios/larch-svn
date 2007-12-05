#! /bin/bash
#
# larch-setup.sh
#
# Author: Michael Towers <gradgrind[at]online[dot]de>
#
# This file is part of the larch project.
#
#    larch is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    larch is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with larch; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#----------------------------------------------------------------------------
# 2007.12.04


if [ "$1" = "-h" ]; then
    echo "larch-setup.sh -h"
    echo "        # Display this information."
    echo "larch-setup.sh"
    echo "        # Set up a larch build environment in the current directory."
    echo "        # x86_64 should be detected automatically."
    echo
    echo "This script fetches and unpacks larch, so that 'mklarch', etc.,"
    echo "can be run from this directory, without installing."
    echo "It also generates appropriate soft links."
    echo
    echo "If there is no pacman in the PATH, a package can be fetched from"
    echo "an Arch server and a statically linked pacman extracted to larch/bin."
    echo "Also repo-add is extracted there and a pacman.conf is generated in"
    echo "the current directory, presenting a dialog for choosing the package"
    echo "server."
    echo "You can avoid fetching a pacman package using ftp by placing one in"
    echo "the current directory. You can use an existing pacman.conf by placing"
    echo "this in the current directory."
    echo
    exit
fi

sysarch="$( uname -m )"
if [ "${sysarch}" != "x86_64" ]; then
    sysarch="i686"
fi

#REPO="ftp://archie.dotsrc.org/projects/archie/larch/testing"
#REPO="http://www.faunos.com/larch/testing"
#REPO="file:///home/larch/testing"
REPO=""

archcore="ftp://ftp.archlinux.org/core/os \
          ftp://ftp.heanet.ie/mirrors/ftp.archlinux.org/core/os \
          ftp://ftp.belnet.be/packages/archlinux/core/os"

# Get path to this directory, via the location of this script
fullpath="$( readlink -f $0 )"
scriptdir="$( dirname ${fullpath} )"

# Just in case ...
cd ${scriptdir}

if [ -d larch ]; then
    echo "ERROR: larch directory exists already"
    exit 1
fi

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
if [ -n "${REPO}" ]; then
    cd tmp
    fetch larch.db.tar.gz
    tar -xzf larch.db.tar.gz
    d=$( ls | grep "^larch-" )
    larchpak=$( grep -A 1 -e "%FILENAME%" ${d}/desc | grep -v "%" )
    rm -rf tmp/*
    fetch ${larchpak}
else
    larchpak=$( ls larch-*.pkg.tar.gz )
    cp ${larchpak} tmp
    cd tmp
fi
tar -xzf ${larchpak}
cd ${scriptdir}
path=$( find tmp -name mklarch )
root=$( dirname $( dirname ${path} ) )
rm -rf larch
cp -a ${root} larch
rm -rf tmp

ln -s ${scriptdir}/larch/bin/mklarch mklarch
ln -s ${scriptdir}/larch/bin/larchify larchify
ln -s ${scriptdir}/larch/bin/inpacs inpacs
ln -s ${scriptdir}/larch/bin/usb2bootiso usb2bootiso

# Check that pacman is available.
if ! which pacman &>/dev/null; then
    # Fetch the pacman package from an Arch server if there isn't one
    # in the current directory
    for serv in ${archcore}; do
        if [ -f pacman*.pkg.tar.gz ]; then break; fi
        wget ${serv}/${sysarch}/pacman*.pkg.tar.gz
    done
    pf=pacman*.pkg.tar.gz
    if ! [ -f ${pf} ]; then
        echo "ERROR: couldn't fetch pacman package"
        exit 1
    fi
    # Extract the needed files from the package
    tar -xzf ${pf} -O usr/bin/pacman.static >larch/bin/pacman
    chmod 755 larch/bin/pacman
    tar -xzf ${pf} -O usr/bin/repo-add >larch/bin/repo-add
    chmod 755 larch/bin/repo-add
    tar -xzf ${pf} -O etc/pacman.d/core >repolist
    if ! [ -f pacman.conf ]; then
        tar -xzf ${pf} -O etc/pacman.conf >pacman.conf
        # Select a package server
        larch/bin/getPackageServer -i repolist pacman.conf
    fi
fi

