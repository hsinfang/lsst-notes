#!/usr/bin/env python
import os
import sqlite3
import lsst.utils
import lsst.daf.persistence as dafPersist

repo = "path/to/the/repo"
butler = dafPersist.Butler(repo)

conn = sqlite3.connect('summary.sqlite3')
cur = conn.cursor()
# Create one table for each datasetType
tables1 = ["deepCoadd_calexp", "deepCoadd_det", "deepCoadd_calexp_background"]
tables1 += ["deepCoadd_meas", "deepCoadd_measMatch", "deepCoadd_measMatchFull", "deepCoadd_forced_src"]
tables = tables1 + ["deepCoadd_mergeDet", "deepCoadd_ref"]
for table in tables:
    cur.execute("drop table if exists %s" % table)
    columns = {'tract': 'int', 'patch': 'str', 'filter': 'str', 'exist': 'int'}
    cmd = "create table %s (id integer primary key autoincrement, " % table
    cmd += ",".join([("%s %s" % (col, colType)) for col, colType in columns.items()])
    cmd += ")"
    conn.execute(cmd)
    conn.commit()

filters = ["HSC-G", "HSC-I", "HSC-R", "HSC-Y", "HSC-Z", "NB0921"]
tracts = [9813, 9697, 9615]

skyMap = butler.get("deepCoadd_skyMap", {})
### skyMap[0][3,3].getIndex() ## is a tuple (3,3)
for filterId in filters:
    for tractId in tracts:
        print("%s %s" % (filterId,tractId))
        for patch in skyMap[tractId]:
            patchId ="%d,%d" % patch.getIndex()
            for table in tables1:
                try:
                    exist = butler.datasetExists(table, tract=tractId, patch=patchId, filter=filterId)
                except dafPersist.butlerExceptions.NoResults:
                    # likely those dataId are not included in the root registry
                    print("butler NoResults %s %s %s %s" % (table, tractId, patchId, filterId))
                    continue
                cmd = "insert into %s (tract, patch, filter, exist) values ('%d', '%s', '%s', '%d')" % (table, tractId, patchId, filterId, exist)
                conn.execute(cmd)

for tractId in tracts:
    filterId=None
    print("%s" % (tractId))
    for patch in skyMap[tractId]:
        patchId ="%d,%d" % patch.getIndex()
        for table in ["deepCoadd_mergeDet", "deepCoadd_ref"]:
            try:
                exist = butler.datasetExists(table, tract=tractId, patch=patchId)
            except dafPersist.butlerExceptions.NoResults:
                # likely those dataId are not included in the root registry
                print("butler NoResults %s %s %s %s" % (table, tractId, patchId, filterId))
                continue
            cmd = "insert into %s (tract, patch, filter, exist) values ('%d', '%s', '%s', '%d')" % (table, tractId, patchId, filterId, exist)
            conn.execute(cmd)

conn.commit()
conn.close()
