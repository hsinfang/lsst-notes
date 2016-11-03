#!/usr/bin/env python
import os
import Pegasus.DAX3 as peg

import lsst.daf.persistence as dafPersist
import lsst.log
import lsst.utils
from lsst.obs.test.testMapper import TestMapper

logger = lsst.log.Log.getLogger("workflow")
logger.setLevel(lsst.log.DEBUG)

# hard-coded output repo
# A local output repo is written when running this script;
# this local repois not used at all for actual job submission and run.
# Real submitted run dumps output in scratch (specified in the site catalog).
outPath = 'peg'
logger.debug("outPath: %s",outPath)

obsTestDir = lsst.utils.getPackageDir('obs_test')
inputDir = os.path.join(obsTestDir, "data", "input")
# Construct these butler and mappers only for creating dax, not for actual runs.
inputArgs = dafPersist.RepositoryArgs(mode='r', mapper=TestMapper, root=inputDir) # read-only input
outputArgs = dafPersist.RepositoryArgs(mode='w', mapper=TestMapper, root=outPath) # write-only output
butler = dafPersist.Butler(inputs=inputArgs, outputs=outPath)
mapperInput = TestMapper(root=inputDir)
mapper = TestMapper(root=inputDir, outputRoot=outPath)

dax = peg.ADAG("ProcessCcdDax")

for visit in range(1, 4):
    filePathRaw = mapperInput.map_raw({'visit': visit}).getLocations()[0]
    inputRaw = peg.File(os.path.basename(filePathRaw))
    inputRaw.addPFN(peg.PFN(filePathRaw, site="local"))
    logger.debug("visit %s input filePathRaw: %s", visit, filePathRaw)
    dax.addFile(inputRaw)

    task = peg.Job(name="processCcd")
    task.addArguments(inputDir, "--output", outPath, "--no-versions",
                      "--id", "visit=%d" % visit)
    task.uses(inputRaw, link=peg.Link.INPUT)

    # Hack to get a full set of dataIds (including both visit and filter)
    dataIdOutput = butler.dataRef("calexp", visit=visit).dataId

    filePathCalexp = mapper.map_calexp(dataIdOutput).getLocations()[0]
    calexp = peg.File(filePathCalexp)
    calexp.addPFN(peg.PFN(filePathCalexp, site="local"))
    logger.debug("visit %s output filePathCalexp: %s", visit, filePathCalexp)

    filePathSrc = mapper.map_src(dataIdOutput).getLocations()[0]
    src = peg.File(filePathSrc)
    src.addPFN(peg.PFN(filePathSrc, site="local"))
    logger.debug("visit %s output filePathSrc: %s", visit, filePathSrc)

    task.uses(calexp, link=peg.Link.OUTPUT, transfer=True, register=True)
    task.uses(src, link=peg.Link.OUTPUT, transfer=True, register=True)
    dax.addJob(task)


f = open("processCcd.dax", "w")
dax.writeXML(f)
f.close()
