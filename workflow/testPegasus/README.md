Links
-----

https://pegasus.isi.edu/documentation/


Sanity Check
------------

- HTCondor is required: e.g. condor_q and condor_status run


Steps
-----

- python generateDaxHelloWorld.py > test.dax

- For running jobs on the worker nodes of the LSST Verification Cluster,
  first allocate nodes using tools in ctrl_execute and obtain a node set name.
  Set env var `NODESET` to that name:
  ```
  export NODESET=${USER}_`cat ~/.lsst/node-set.seq`
  ```

- ./plan_dax_hello.sh test.dax
