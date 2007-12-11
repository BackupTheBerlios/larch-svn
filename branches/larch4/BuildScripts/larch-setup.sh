#!/bin/sh

echo
echo "This script fetches and unpacks pacin and larch, so that 'mklarch' can"
echo "be run from this directory, without installing."
echo "It also generates a wrapper script 'mklarch' which should"
echo "then be used instead of the real 'mklarch' script."
echo

REPO="ftp://archie.dotsrc.org/projects/archie/larch/larch4"
#REPO="http://www.faunos.com/larch/larch4"
#REPO="file:///home/larch/larch4"

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
d=$( ls | grep "^larch-" )
larchpak=$( grep -A 1 -e "%FILENAME%" ${d}/desc | grep -v "%" )
d=$( ls | grep "^pacin-" )
pacinpak=$( grep -A 1 -e "%FILENAME%" ${d}/desc | grep -v "%" )
cd ..

rm -rf tmp
mkdir tmp
cd tmp
fetch ${pacinpak}
fetch ${larchpak}
tar -xzf ${pacinpak}
tar -xzf ${larchpak}
cd ${scriptdir}
path=$( find tmp -name mklarch )
root=$( dirname $( dirname ${path} ) )
rm -rf larch
cp -a ${root} larch
rm -rf tmp

cat >mklarch <<EOT
#!/bin/sh
export LARCHREPO=${REPO}
${scriptdir}/larch/bin/mklarch \$*
EOT

chmod 755 mklarch

cp ${scriptdir}/larch/share/larch/config_larch ${scriptdir}
ln -s ${scriptdir}/larch/bin/pacin pacin
ln -s ${scriptdir}/larch/bin/usb2bootiso usb2bootiso
