#!/usr/bin/env python
#
# beyond lsst_distrib, setup pipe_supertask

import os
import Pegasus.DAX3 as peg

import lsst.daf.persistence as dafPersist
import lsst.log
import lsst.utils
from lsst.obs.test.testMapper import TestMapper

obsTestDir = lsst.utils.getPackageDir('obs_test')
InputDir = os.path.join(obsTestDir, "data", "input")
outPath = 'peg'
butler = dafPersist.Butler(InputDir)

dax = peg.ADAG("example")

for visit in range(1, 4):
    inputRaw = peg.File("file.raw.visit%d" % visit)
    filePath = TestMapper(root=InputDir).map_raw({'visit': visit}).getLocations()[0]
    inputRaw.addPFN(peg.PFN(filePath, site="local"))
    dax.addFile(inputRaw)
    exampleCmdLineTask = peg.Job(name="activator")
    exampleCmdLineTask.addArguments("exampleCmdLineTask", "--extras", InputDir,
                                    "--output", outPath, "--no-versions", "--id", "visit=%d" % visit)
    exampleCmdLineTask.uses(inputRaw, link=peg.Link.INPUT)

    result = peg.File("exampleOutput.visit%d" % visit)
    exampleCmdLineTask.setStderr(result)
    exampleCmdLineTask.uses(result, link=peg.Link.OUTPUT, transfer=True, register=True)
    dax.addJob(exampleCmdLineTask)


f = open("testdaxfile.dax", "w")
dax.writeXML(f)
f.close()
