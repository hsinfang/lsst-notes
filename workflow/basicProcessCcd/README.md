Setup
-----

- Setup the LSST Stack lsst_apps
- Modify sites.xml and tc.txt as necessary
- Set env var `WORKFLOW_HOME` to the root dir of this git repo, e.g.:
  ```
  export WORKFLOW_HOME=`git rev-parse --show-toplevel`
  ```

- For running jobs on the worker nodes of the LSST Verification Cluster,
  first allocate nodes using tools in ctrl_execute and obtain a node set name.
  Set env var `NODESET` to that name:
  ```
  export NODESET=${USER}_`cat ~/.lsst/node-set.seq`
  ```


Steps
-----

- python generateDaxExampleTask.py
- ./plan_dax.sh processCcd.dax


To plot DAX and DAG
-------------------

- pegasus-plots -o plotsDir -p dax_graph submit/centos/pegasus/ProcessCcdDax/run0001/
- pegasus-plots -o plotsDir -p dag_graph submit/centos/pegasus/ProcessCcdDax/run0001/
