# OSIP-KB-ICE: System Engineering Models Meet Knowledge Graphs

The aim of this repository is to collect the source code of the activity "System Engineering Models meet Knowledge Graphs", OSIP ESA Contract No. 4000133311/20/NL/GLC, Strathclyde RKES REF 200980. The expected deliverables are:
* **SW1**: Schema of the Vaticle Knowledge Graph (KG), migrated from the ECSS-E-TM-10-25A Annex A UML model and enriched with metadata.
* **SW2**: Pipelines to automatically populate a Vaticle Knowledge Graph with Engineering Models based on the ECSS-E-TM-10-25A TM and rules to infer implicit knowledge, including a similarity analysis.

## SW1: Generate a TypeDB Schema written in TypeQL from the ECSS-E-TM-10-25A Annex A UML model
### The SW1 includes:
in `schema_generation`:
* `xmi2typeql.py`: the functions to map the UML classes, properties, relations to TypeQL entities, attributes and relations
* `xmi2typeql_data_v2_0_1.py`: the template to write TypeQL types called by `xmi2typeql.py`, compatible with TypeDB v2.0.1 up to v2.10.1
* `TypeDBSchemaECSS.tql`: the TypeDB schema compatible with TypeDB v2.10.1, generated with `xmi2typeql.py`and `xmi2typeql_data_v2_0_1.py`
* `defineMetadata.tql`: an additional schema definition to enrich the KG with metadata


## SW2: Population of TypeDB Graph and Inference
### The SW2 includes:
in `/knowledge_graph`: 
* `migrate_em_json.py`: Script to (i) automatically create a new TypeDB database, 
(ii) define  the ECSS-based TypeDB schema and additional rules, 
(iii) populate it with the .json files of Engineering Models, 
and (iv) insert metadata.
* `migrationTemplate.py`: Templates to generate insert queries for each type of entities.
* `similarityMetadata.py`: Script to (i) extract metadata from TypeDB, (ii) compute the similarity factors between each iterations, 
 and (iii) insert new relations with the factor values as attributes.
* `similarityElements.py`: Script to extract Elements and calculate Jaccard similarity between their containing parameters
                           + cosine similarity between their names
* `main.py` : Main running all scripts all necessary steps 
 
in `recommendation`
* `Notebook_recommendation.ipynb`: Notebook for running the similarity analysis with a new mission


For SW2 respective docker-files are available in `/knowledge_graph` to run the KG population automatically, 
as well as in `/recommendation` to provide a Jupyterlab-image to run the analysis. 
In order to run SW2, it is not necessary to run SW1 first. The modified output of SW1 is provided in SW2. 
Therefore, it is recommended to skip the steps of SW1 and start with the KG population in `/knowledge_graph` directly.

### Pre installation steps for SW2:
- install docker-desktop on machine (tested on Docker Engine v20.10.13, Docker Compose version v2.3.3)
- git clone https://gitlab.esa.int/Luis.Mansilla/osip-kb-ice.git
- **insert Engineering model (EM) files into `app/datasets/`**
- **insert metadata files into `app/Metadata/`**

## Licensing information
Information about the licenses of the used Python packages for SW2 can be found in the file `package_licenses.txt`.

## Team
ESA T.O.: Serge Valera, serge.valera@esa.int  
ESA Support: Luis Mansilla,Audrey Berquand, Alberto Gonzalez Fernandez  
Contractor: University of Strathclyde  
Contractor team: Paul Darm, Annalisa Riccardi, Audrey Berquand, Edmondo Minisci




