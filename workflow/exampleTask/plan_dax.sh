#!/bin/bash

DIR=$(cd $(dirname $0) && pwd)

if [ $# -ne 1 ]; then
    echo "Usage: $0 DAXFILE"
    exit 1
fi

DAXFILE=$1

# Check if pipe_supertask is set up
cmdLineActivator -lp
echo `which cmdLineActivator`

# This command tells Pegasus to plan the workflow contained in 
# dax file passed as an argument. The planned workflow will be stored
# in the "submit" directory. The execution # site is "".
# --input-dir tells Pegasus where to find workflow input files.
# --output-dir tells Pegasus where to place workflow output files.
pegasus-plan \
    -Dpegasus.catalog.site.file=sites.xml \
    -Dpegasus.catalog.transformation.file=tc.txt \
    -Dpegasus.register=false \
    -Dpegasus.data.configuration=sharedfs \
    --output-dir $DIR/output \
    --dir $DIR/submit \
    --dax $DAXFILE \
    --submit 
