# OSIP-KB-ICE: System Engineering Models Meet Knowledge Graphs

* **SW2**: Pipelines to automatically populate a Vaticle Knowledge Graph with Engineering Models based on the ECSS-E-TM-10-25A TM 
and rules to expand the schema, including a similarity analysis between EMs and Elements in the EMs.

This file concentrates on how to define the schema, insert the data, and calculate the similarities in the KG with a docker build.

## Pre installation steps:
- install docker on machine (tested on Docker Engine v20.10.13, Docker Compose version v2.3.3)
- git clone https://gitlab.esa.int/Luis.Mansilla/osip-kb-ice.git
- **insert Engineering model (EM) files into `app/datasets/`**
- **insert metadata files into `app/Metadata/`**


**Note: The following procedures can be run without the running `schema_generation` beforehand. A modified version of the schema file can be found in `app/TypdeDB/schema`.** 

## KG Installation procedure 

- *Make sure Docker-Desktop is running*
- Navigate with command line tool (`cmd`) on your machine into folder `.../knowledge_graph`
- Run in command line tool `docker compose build`
- Run in command line tool `docker compose run data_insertion`, take a walk (depending on how many EMs are being inserted, this process can take multiple hours)

If for some reason docker exits the script, run `docker compose run data_insertion` again. The data insertion process should start over again, and recognise by itself when it has to add data again. 

*Advanced usage: "Dockerfile" gives specific instructions to `main.py` on what steps to perform (schema definition, data insertion, metadata_dir) it can be opened with editor software and these commands can be changed.*

Alternatively, one can also run `main.py` with a running TypeDB server (V2.8.1) to install the KG. 

## Querying after Installation

The inserted data in the KG can be queried e.g. through the natively shipped *"TybeDB console"*. 
For accessing the console and running TypeDB queries run the following commands:

- *Make sure tybedb container is running with command `docker compose ps` (depending on used OS should be named `knowledge_graph_typedb_1` or `knowledge_graph-typedb_1`), if not running, run command `docker compose up typebdb`*
- Run in another command line window `docker compose exec typedb /opt/typedb-all-linux/typedb console`, which starts the console for TypeDB
- Run `transaction <KG_name> data read`, with `<KG_name>` specifying the name of the KG to query (in the standard setting `ESAEMs`)
- Now you can run queries against the KG, example queries are provided in `./app/TypeDB_example_queries`

Another way interacting with the KG is using the visualisation tool of TypeDB, which can be downloaded following this link: https://vaticle.com/download#typedb-studio

The third way is using the Python client of TypeDB. This is shown for the automatic similarity analysis in the 
notebook in `../recommendation/notebook`. To run the analysis follow the instructions in the folder `../recommendation/`. 

## Team
ESA T.O.: Serge Valera, serge.valera@esa.int  
ESA Support: Luis Mansilla, Quirien Wijnands,  Alberto Gonzalez Fernandez  
Contractor: University of Strathclyde  
Contractor team: Paul Darm, Annalisa Riccardi, Audrey Berquand, Edmondo Minisci,  


