Setup
-----

- Setup the LSST Stack lsst_apps and pipe_supertask

- Modify sites.xml and tc.txt as necessary

- For running jobs on the worker nodes of the LSST Verification Cluster,
  first allocate nodes using tools in ctrl_execute and obtain a node set name.
  Set env var `NODESET` to that name:
  ```
  export NODESET=${USER}_`cat ~/.lsst/node-set.seq`
  ```

Steps
-----

- python generateDaxExampleTask.py

- ./plan_dax.sh testdaxfile.dax 
