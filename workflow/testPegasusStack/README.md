Steps
-----

- python generateDaxHelloWorld.py > test.dax

- Set env var `WORKFLOW_HOME` to the root dir of this git repo, e.g.:
  ```
  export WORKFLOW_HOME=`git rev-parse --show-toplevel`
  ```

- ./plan_dax_hello.sh test.dax 

- For running jobs on the worker nodes of the LSST Verification Cluster,
  first allocate nodes using tools in ctrl_execute and obtain a node set name.
  Set env var `NODESET` to that name:
  ```
  export NODESET=${USER}_`cat ~/.lsst/node-set.seq`
  ```
