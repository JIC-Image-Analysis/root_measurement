export DESTDIR=~/packages
mkdir -p $DESTDIR
wget https://downloads.openmicroscopy.org/bio-formats/6.6.0/artifacts/bftools.zip -O $DESTDIR/bftools.zip
unzip $DESTDIR/bftools.zip -d $DESTDIR
