#!/usr/bin/env python
import os
import Pegasus.DAX3 as peg

import lsst.daf.persistence as dafPersist
import lsst.log
import lsst.utils
from lsst.obs.hsc.hscMapper import HscMapper
from inputData import *

logger = lsst.log.Log.getLogger("workflow")
logger.setLevel(lsst.log.DEBUG)

# hard-coded output repo
# A local output repo is written when running this script;
# this local repo is not used at all for actual job submission and run.
# Real submitted run dumps output in scratch (specified in the site catalog).
outPath = 'peg'
logger.debug("outPath: %s", outPath)

# Assuming ci_hsc has been run beforehand and the data repo has been created
ciHscDir = lsst.utils.getPackageDir('ci_hsc')
inputRepo = os.path.join(ciHscDir, "DATA")
calibRepo = os.path.join(inputRepo, "CALIB")

# Construct these butler and mappers only for creating dax, not for actual runs.
inputArgs = dafPersist.RepositoryArgs(mode='r', mapper=HscMapper, root=inputRepo)  # read-only input
outputArgs = dafPersist.RepositoryArgs(mode='w', mapper=HscMapper, root=outPath)  # write-only output
butler = dafPersist.Butler(inputs=inputArgs, outputs=outPath)
mapperInput = HscMapper(root=inputRepo)
mapper = HscMapper(root=inputRepo, outputRoot=outPath)

dax = peg.ADAG("CiHscDax")

filePathMapper = os.path.join(inputRepo, "_mapper")
mapperFile = peg.File(os.path.join(outPath, "_mapper"))
mapperFile.addPFN(peg.PFN(filePathMapper, site="local"))
dax.addFile(mapperFile)

filePathRegistry = os.path.join(inputRepo, "registry.sqlite3")
registry = peg.File(os.path.join(outPath, "registry.sqlite3"))
registry.addPFN(peg.PFN(filePathRegistry, site="local"))
dax.addFile(registry)

filePathCalibRegistry = os.path.join(calibRepo, "calibRegistry.sqlite3")
calibRegistry = peg.File(os.path.join(outPath, "calibRegistry.sqlite3"))
calibRegistry.addPFN(peg.PFN(filePathCalibRegistry, site="local"))
dax.addFile(calibRegistry)

calexpList = []
tasksProcessCcdList = []

for data in sum(allData.itervalues(), []):
    logger.debug("processCcd dataId: %s", data.dataId)

    processCcd = peg.Job(name="processCcd")
    processCcd.addArguments(outPath, "--calib", outPath, "--output", outPath, "--no-versions",
                            data.id())
    processCcd.uses(registry, link=peg.Link.INPUT)
    processCcd.uses(calibRegistry, link=peg.Link.INPUT)
    processCcd.uses(mapperFile, link=peg.Link.INPUT)

    filePath = mapperInput.map_raw(data.dataId).getLocations()[0]
    lfn = filePath.replace(inputRepo, outPath)
    infile = peg.File(lfn)
    infile.addPFN(peg.PFN(filePath, site="local"))
    logger.debug("%s: input: %s -> %s", data.name, filePath, lfn)
    dax.addFile(infile)
    processCcd.uses(infile, link=peg.Link.INPUT)
    for inputType in ["bias", "dark", "flat", "bfKernel"]:
        mapFunc = getattr(mapperInput, "map_"+inputType)
        filePath = mapFunc(data.dataId).getLocations()[0]
        lfn = filePath.replace(calibRepo, outPath)
        infile = peg.File(lfn)
        infile.addPFN(peg.PFN(filePath, site="local"))
        logger.debug("%s: input: %s -> %s", data.name, filePath, lfn)
        if not dax.hasFile(infile):
            dax.addFile(infile)
        processCcd.uses(infile, link=peg.Link.INPUT)

    filePathCalexp = mapper.map_calexp(data.dataId).getLocations()[0]
    calexp = peg.File(filePathCalexp)
    calexp.addPFN(peg.PFN(filePathCalexp, site="local"))
    logger.debug("dataId %s output filePathCalexp: %s", data.name, filePathCalexp)

    filePathSrc = mapper.map_src(data.dataId).getLocations()[0]
    src = peg.File(filePathSrc)
    src.addPFN(peg.PFN(filePathSrc, site="local"))
    logger.debug("dataId %s output filePathSrc: %s", data.name, filePathSrc)

    processCcd.uses(calexp, link=peg.Link.OUTPUT, transfer=True, register=True)
    processCcd.uses(src, link=peg.Link.OUTPUT, transfer=True, register=True)

    logProcessCcd = peg.File("logProcessCcd.%s" % data.name)
    processCcd.setStderr(logProcessCcd)
    processCcd.uses(logProcessCcd, link=peg.Link.OUTPUT)

    dax.addJob(processCcd)

    calexpList.append(calexp)
    tasksProcessCcdList.append(processCcd)

# Get the skymap config from ci_hsc package
filePathSkymap = os.path.join(ciHscDir, "skymap.py")
skymapConfig = peg.File("skymap.py")
skymapConfig.addPFN(peg.PFN(filePathSkymap, site="local"))
dax.addFile(skymapConfig)

makeSkyMap = peg.Job(name="makeSkyMap")
makeSkyMap.uses(mapperFile, link=peg.Link.INPUT)
makeSkyMap.uses(registry, link=peg.Link.INPUT)
makeSkyMap.uses(skymapConfig, link=peg.Link.INPUT)
makeSkyMap.addArguments(outPath, "--output", outPath, "-C", skymapConfig, "--no-versions")
logMakeSkyMap = peg.File("logMakeSkyMap")
makeSkyMap.setStderr(logMakeSkyMap)
makeSkyMap.uses(logMakeSkyMap, link=peg.Link.OUTPUT)

filePathSkyMap = mapper.map_deepCoadd_skyMap({}).getLocations()[0]
skyMap = peg.File(filePathSkyMap)
skyMap.addPFN(peg.PFN(filePathSkyMap, site="local"))
logger.debug("filePathSkyMap: %s", filePathSkyMap)
makeSkyMap.uses(skyMap, link=peg.Link.OUTPUT, transfer=True, register=True)

dax.addJob(makeSkyMap)

f = open("ciHsc.dax", "w")
dax.writeXML(f)
f.close()
