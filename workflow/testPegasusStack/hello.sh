#!/usr/bin/env bash

OUTFILE=$1
mkdir -p `dirname $OUTFILE`
echo "AFW: " $AFW_DIR >> $OUTFILE
echo "OBS_TEST: " $OBS_TEST_DIR >> $OUTFILE
echo "python: " `which python` >> $OUTFILE
python -c 'import lsst.afw'
#python -c 'import lsst.pipe.supertask'

# make more dummy products and ignore cleaning up
BUTLER="repo/structure/traces"
mkdir -p `dirname $BUTLER`
echo "python: " `which python` >> $BUTLER
