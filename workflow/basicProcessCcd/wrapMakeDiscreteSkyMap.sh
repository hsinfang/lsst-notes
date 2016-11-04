#!/bin/bash
#
# e.g. to test:
# wrapMakeDiscreteSkyMap.sh outPath --output outPath --id visit=1 filter=g --id visit=2 filter=g

mkdir -p $1
echo "lsst.obs.test.testMapper.TestMapper" > $1/_mapper
makeDiscreteSkyMap.py "$@"
