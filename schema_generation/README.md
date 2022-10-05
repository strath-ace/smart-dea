# OSIP-KB-ICE: System Engineering Models Meet Knowledge Graphs

The aim of this repository is to collect the source code of the activity "System Engineering Models meet Knowledge Graphs", OSIP ESA Contract No. 4000133311/20/NL/GLC, Strathclyde RKES REF 200980. The expected deliverables are:
* **SW1**: Schema of the Vaticle Knowledge Graph (KG), migrated from the ECSS-E-TM-10-25A Annex A UML model and enriched with metadata.
* **SW2**: Pipelines to automatically populate a Vaticle Knowledge Graph with Engineering Models based on the ECSS-E-TM-10-25A TM and rules to infer implicit knowledge, including a similarity analysis.

## SW1: Generate a TypeDB Schema written in TypeQL from the ECSS-E-TM-10-25A Annex A UML model
The SW1 includes:
* `xmi2typeql.py`: the functions to map the UML classes, properties, relations to TypeQL entities, attributes and relations
* `xmi2typeql_data_v2_0_1.py`: the template to write TypeQL types called by `xmi2typeql.py`, compatible with TypeDB version 2.8.1
* `TypeDBSchemaECSS.tql`: the TypeDB schema compatible with TypeDB v2.8.1, generated with `xmi2typeql.py`and `xmi2typeql_data_v2_0_1.py`
* `defineMetadata.tql`: an additional schema definition to enrich the KG with metadata, compatible with TypeDB v2.0.1

The above schemas were generated with `xmi_verter`version 0.9.1 for the ECSS_E_TM_10_25A Annex A version 2.4.1.
The following paragraphs explain how to reproduce the TypeDB schemas and how to load them in a Vaticle Knowledge Graph.

### Generate TypeDB Schema

#### Prerequisities
* Visual Studio (VS) 2017 (to run `xmi_verter.py`)
* `xmi_verter` and `EM-10-25A` folders cloned or downloaded from the [OCDT GitLab](https://gitlab.esa.int/). (Access may need to be required)

#### Installation
A. **Set up the VS environment to Python v2.7 (required to run `xmi_verter`)**

The following Python (v2.7) packages need to be installed:
- Graphviz `dot` v2.28.0 or higher
- pydot v1.2.2 or higher, see https://pypi.python.org/pypi/pydot/ . Used to generate Graphviz dot language files from Python.
- xlutils, see https://pypi.python.org/pypi/xlutils/ . Used for creation of Excel workbooks

B. **Add xmi2typeql pipeline to `xmi_verter.py`**
  * Add `xmi2typeql.py` and `xmi2typeql_data_v2_0_1.py` to the `xmi_verter` folder (you might also have to manually add it to the solution in Visual Studio)
  * At the start of the code, with all other Generator imports, add `from xmi2typeql import TypeQLGenerator`
  * after `JsonMetaModelGenerator().generate(model, generatedCodePath)`, add `TypeQLGenerator().generate(model, generatedCodePath)`

*Important Comment: Make sure that `xmi_verter.ini` contains all the following paths:
`xmi_file = ..\..\e-tm-10-25\annex-a\ECSS_E_TM_10_25.mdxml`
`package_list = CommonData,SiteDirectoryData,EngineeringModelData`
`documentation_path = ..\..\e-tm-10-25\annex-a\ECSS_E_TM_10_25_reference_manual`
`generated_code_path = ..\..\e-tm-10-25\annex-a\ECSS_E_TM_10_25_generated`
The documentation_path and generated_code_path might be missing, an issue has been raised on OCDT GitLab.*

C. **You're all set! Time to run `xmi_verter.py`!**

The resulting TypeDB schema is stored in `e-tm-10-25\annex-a\ECSS_E_TM_10_25_generated`. It should take around 6 seconds to run.


## Team
ESA T.O.: Serge Valera, serge.valera@esa.int  
ESA Support: Quirien Wijnands, Luis Mansilla, Alberto Gonzalez Fernandez  
Contractor: University of Strathclyde  
Contractor team: Annalisa Riccardi, Audrey Berquand, Edmondo Minisci, Paul Darm  




