#!/usr/bin/env python
import os
import sqlite3
import lsst.utils
import lsst.daf.persistence as dafPersist

repo = "path/to/the/repo"
butler = dafPersist.Butler(repo)

with open('path/to/visit/list/file') as f:
    visits = f.read().splitlines()

conn = sqlite3.connect('summary.sqlite3')
cur = conn.cursor()
# Create one table for each datasetType
tables = ["calexp", "src", "skyCorr"]
for table in tables:
    cur.execute("drop table if exists %s" % table)
    columns = {'visit': 'int', 'ccd': 'int', 'exist': 'int'}
    cmd = "create table %s (id integer primary key autoincrement, " % table
    cmd += ",".join([("%s %s" % (col, colType)) for col, colType in columns.items()])
    cmd += ")"
    conn.execute(cmd)
    conn.commit()

for visitStr in visits:
    visit = int(visitStr)
    for ccd in range(104):
        if ccd == 9: continue
        for table in tables:
            try:
                exist = butler.datasetExists(table, visit=visit, ccd=ccd)
            except dafPersist.butlerExceptions.NoResults:
                # likely those dataId are not included in the root registry
                print("butler NoResults %s %s %s" % (table, visit, ccd))
                continue
            cmd = "insert into %s (visit, ccd, exist) values ('%d', '%d', '%d')" % (table, visit, ccd, exist)
            conn.execute(cmd)

conn.commit()
conn.close()
