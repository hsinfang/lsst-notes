#!/usr/bin/env python
import argparse
import os
import sqlite3
import lsst.utils
import lsst.daf.persistence as dafPersist
import lsst.afw.image as afwImage
import lsst.afw.geom as afwGeom


parser = argparse.ArgumentParser(description='Build a sqlite3 with patches overlapped by calexps')
parser.add_argument("repo", type=str,
                    help="a Butler repo root path")
parser.add_argument("-i", "--input", type=str, default="visitsTest.txt",
                    help='a file containing a list of visit IDs')
parser.add_argument("-o", "--output", type=str, default="overlaps.sqlite3",
                    help="file name for the output sqlite3")
args = parser.parse_args()

butler = dafPersist.Butler(args.repo)

with open(args.input) as f:
    visits = f.read().splitlines()

conn = sqlite3.connect(args.output)
cur = conn.cursor()
# Create one table for each datasetType
tables = ["calexp", ]
for table in tables:
    cur.execute("drop table if exists %s" % table)
    columns = {'visit': 'int', 'ccd': 'int', 'exist': 'int', 'tract': 'int', 'patch': 'str', 'ra': 'float', 'dec': 'float', 'filter': 'str'}
    cmd = "create table %s (id integer primary key autoincrement, " % table
    cmd += ",".join([("%s %s" % (col, colType)) for col, colType in columns.items()])
    cmd += ")"
    conn.execute(cmd)
    conn.commit()

skymap = butler.get("deepCoadd_skyMap", {})
for visitStr in visits:
    visit = int(visitStr)
    for ccd in range(104):
        for table in tables:

            try:
                exist = butler.datasetExists(table, visit=visit, ccd=ccd)
            except dafPersist.butlerExceptions.NoResults:
                # likely those dataId are not included in the root registry
                print "butler NoResults %s %s %s" % (table, visit, ccd)
                continue

            if exist:
                filterName = butler.queryMetadata(datasetType='raw', format=("filter",), dataId={'visit':visit})[0]
                md = butler.get("calexp_md", visit=visit, ccd=ccd)
                wcs = afwImage.makeWcs(md)
                nx, ny = md.get("NAXIS1"), md.get("NAXIS2")
                imageBox = afwGeom.Box2D(afwGeom.Point2D(0, 0), afwGeom.Extent2D(nx, ny))
                imageCorners = [wcs.pixelToSky(pix) for pix in imageBox.getCorners()]
                imageCenter = wcs.pixelToSky(imageBox.getCenter())
                ctrRa = imageCenter.getRa().asDegrees()
                ctrDec = imageCenter.getDec().asDegrees()
                # c.f. # skymap[9010].getCtrCoord().toFk5()

                tractPatchList =  skymap.findTractPatchList(imageCorners)
                for tractInfo, patchInfoList in tractPatchList:
                    for patchInfo in patchInfoList:
                        patchId = '%d,%d' % patchInfo.getIndex()
                        cmd = "insert into %s (visit, ccd, exist, tract, patch, ra, dec, filter) values ('%d', '%d', '%d', '%d', '%s', '%f', '%f', '%s')" % (table, visit, ccd, exist, tractInfo.getId(), patchId, ctrRa, ctrDec, filterName)
                        conn.execute(cmd)

            else:
                cmd = "insert into %s (visit, ccd, exist, tract, patch, ra, dec, filter) values ('%d', '%d', '%d', '%d', '%s', '%f', '%f', '%s')" % (table, visit, ccd, exist, -1, None, -999, -999, None)
                conn.execute(cmd)


conn.commit()
conn.close()
