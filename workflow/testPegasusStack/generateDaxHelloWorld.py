#!/usr/bin/env python
#
import Pegasus.DAX3 as peg
import sys
import os

dax = peg.ADAG("hello")

a = peg.File("f.a")
a.addPFN(peg.PFN("f.a", site="local"))
dax.addFile(a)

hello = peg.Job(name="hello")
hello.uses(a, link=peg.Link.INPUT)
b = peg.File("repo/f.b")
hello.addArguments(b)
hello.uses(b, link=peg.Link.OUTPUT)
dax.addJob(hello)

world = peg.Job("world")
c = peg.File("f.c")
world.uses(b, link=peg.Link.INPUT)
world.addArguments(b)
world.setStdout(c)
world.uses(c, link=peg.Link.OUTPUT)
dax.addJob(world)

dax.addDependency(peg.Dependency(parent=hello, child=world))

dax.writeXML(sys.stdout)
