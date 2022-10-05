# OSIP-KB-ICE: System Engineering Models Meet Knowledge Graphs

The aim of this repository is to collect the source code of the activity "System Engineering Models meet Knowledge Graphs", OSIP ESA Contract No. 4000133311/20/NL/GLC, Strathclyde RKES REF 200980. The expected deliverables are:
* **SW1**: Schema of the Vaticle Knowledge Graph (KG), migrated from the ECSS-E-TM-10-25A Annex A UML model and enriched with metadata.
* **SW2**: Pipelines to automatically populate a Vaticle Knowledge Graph with Engineering Models based on the ECSS-E-TM-10-25A TM and rules to infer implicit knowledge, including a similarity analysis.

This file instructs on how to run the actual similarity analysis of **SW2**.

## Prerequisites

Follow the instructions in `.../knowledge_graph` to install the KG and insert the data.

## Application of similarity analysis

Two ways of running the notebook depending on if *jupyterlab* is installed on the system:

No *jupyterlab* installed on system and running from local machine:

 - If you are running the notebook directly after setting up the KG run `docker stop knowledge_graph_typedb_1` for Windows systems and `docker stop knowledge_graph-typedb_1` for Linux systems
 - Navigate with commandline tool of choice to this folder and enter command `docker-compose up`
 - Go to your internet browser and access jupterlab by typing in `localhost:8888`, the password is `docker`
 
No *jupyterlab* installed on system and running from remote machine:

 - If you are running the notebook directly after setting up the KG run `docker stop knowledge_graph_typedb_1` for Windows systems and `docker stop knowledge_graph-typedb_1` for Linux systems
 - Open `docker-compose-remote.yml` and under `jupyter\ports:` change the line to {your_IP}:8888:8888 (Replace your IP by the IP of the machine you are running docker on e.g. by visiting whatismyip.com) 
 - Navigate with commandline tool of choice to this folder and enter command `docker compose -f docker-compose-remote.yml up`
 - Go to your internet browser and access jupterlab by typing in `{your_IP}:8888`, the password is `docker` 
 - 
 
If *jupyterlab* installed on system

 - Navigate  with commandline tool of choice to this folder and enter command `docker compose build`
 - Navigate  with commandline tool of choice to this folder and enter command `docker compose up typedb`
 - In the Notebook you have to change the parameter `server_address` from `typedb:1729` to `localhost:1729`


## Team
ESA T.O.: Serge Valera, serge.valera@esa.int  
ESA Support: Quirien Wijnands, Luis Mansilla, Alberto Gonzalez Fernandez  
Contractor: University of Strathclyde  
Contractor team: Annalisa Riccardi, Audrey Berquand, Edmondo Minisci, Paul Darm  




