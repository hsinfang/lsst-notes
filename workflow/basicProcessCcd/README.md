Setup
-----

- Setup the LSST Stack lsst_apps
- Modify sites.xml and tc.txt as necessary


Steps
-----

- python generateDaxExampleTask.py
- ./plan_dax.sh processCcd.dax


To plot DAX and DAG
-------------------

- pegasus-plots -o plotsDir -p dax_graph submit/centos/pegasus/ProcessCcdDax/run0001/
- pegasus-plots -o plotsDir -p dag_graph submit/centos/pegasus/ProcessCcdDax/run0001/
