#!/usr/bin/env python
#

print "starting world"

import os

import lsst.afw.image as afwImage
import lsst.utils

obsTestDir = lsst.utils.getPackageDir('obs_test')
fitsPath = os.path.join(obsTestDir, "data", "input", "raw", "raw_v1_fg.fits.gz")
# Load a raw directly and skip standardizing
exp = afwImage.ExposureF(fitsPath)
print exp.getDimensions()

print "ending world"
