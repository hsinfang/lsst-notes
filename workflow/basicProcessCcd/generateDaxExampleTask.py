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

calexpList = []
dataIdStrList = []
tasksProcessCcdList = []

for visit in range(1, 4):
    filePathRaw = mapperInput.map_raw({'visit': visit}).getLocations()[0]
    inputRaw = peg.File(os.path.basename(filePathRaw))
    inputRaw.addPFN(peg.PFN(filePathRaw, site="local"))
    logger.debug("visit %s input filePathRaw: %s", visit, filePathRaw)
    dax.addFile(inputRaw)

    processCcd = peg.Job(name="processCcd")
    processCcd.addArguments(inputDir, "--output", outPath, "--no-versions",
                            "--id", "visit=%d" % visit)
    processCcd.uses(inputRaw, link=peg.Link.INPUT)

    # Hack to get a full set of dataIds (including both visit and filter)
    dataIdOutput = butler.dataRef("calexp", visit=visit).dataId
    logger.debug("processCcd output dataId: %s", dataIdOutput)
    dataIdStrList.append(' '.join("%s=%s" % (key, value) for (key, value) in dataIdOutput.items()))

    filePathCalexp = mapper.map_calexp(dataIdOutput).getLocations()[0]
    calexp = peg.File(filePathCalexp)
    calexp.addPFN(peg.PFN(filePathCalexp, site="local"))
    logger.debug("visit %s output filePathCalexp: %s", visit, filePathCalexp)

    filePathSrc = mapper.map_src(dataIdOutput).getLocations()[0]
    src = peg.File(filePathSrc)
    src.addPFN(peg.PFN(filePathSrc, site="local"))
    logger.debug("visit %s output filePathSrc: %s", visit, filePathSrc)

    processCcd.uses(calexp, link=peg.Link.OUTPUT, transfer=True, register=True)
    processCcd.uses(src, link=peg.Link.OUTPUT, transfer=True, register=True)

    dax.addJob(processCcd)

    calexpList.append(calexp)
    tasksProcessCcdList.append(processCcd)

# For makeSkyMap task, because the input repo is not a linked butler repo:
# wrap makeDiscreteSkyMap so to create a _mapper and please butler;
# specify complete dataId so to remove the need of the registry.
makeSkyMap = peg.Job(name="wrapMakeDiscreteSkyMap")
makeSkyMap.addArguments(outPath, "--output", outPath, "--no-versions",
                        "--id", " --id ".join(dataIdStrList))
logger.debug("Adding makeSkyMap with dataId: %s", dataIdStrList)

for calexp in calexpList:
    makeSkyMap.uses(calexp, link=peg.Link.INPUT)

filePathSkyMap = mapper.map_deepCoadd_skyMap({}).getLocations()[0]
skyMap = peg.File(filePathSkyMap)
skyMap.addPFN(peg.PFN(filePathSkyMap, site="local"))
logger.debug("filePathSkyMap: %s", filePathSkyMap)
makeSkyMap.uses(skyMap, link=peg.Link.OUTPUT, transfer=True, register=True)

dax.addJob(makeSkyMap)
for job in tasksProcessCcdList:
    dax.depends(makeSkyMap, job)

f = open("processCcd.dax", "w")
dax.writeXML(f)
f.close()
