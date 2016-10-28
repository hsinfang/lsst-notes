#!/usr/bin/env bash

echo "AFW: " $AFW_DIR
echo "OBS_TEST: " $OBS_TEST_DIR
echo "python: " `which python`
python -c 'import lsst.afw'
python -c 'import lsst.pipe.supertask'
