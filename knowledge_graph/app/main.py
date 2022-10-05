# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, You can obtain one at https://mozilla.org/MPL/2.0/.
# ----------------        2022 University of Strathclyde and Author ----------------
# -------------------------------- Author: Paul Darm --------------------------------
# ------------------------- e-mail: paul.darm@strath.ac.uk --------------------------
import argparse
import migrate_em_json, similarityMetadata, similarityElements

def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dbName", "-n", type=str, required=True,
        help="Name of Knowledge Graph", default = 'ESAEMs2'
    )
    parser.add_argument(
        "--defineSchema", "-dS",  type=lambda x: (str(x).lower() == 'true'), required=False,
        default = True
    )

    parser.add_argument(
        "--schemaFile", "-sF", type=str, required=False,
        help="Absolute path to TypeDB schema file",
        default ='.\\app\\TypeDB\\schema\\TypeDBSchemaECSS_relunique'
    )
    parser.add_argument(
        "--defineRules", "-dR",  type=lambda x: (str(x).lower() == 'true'), required=False,
        default = True
    )
    parser.add_argument(
        "--rulesFile", "-rF", type=str, required=False,
        help="Absolute path to TypeDB rules file",
        default =".\\app\\TypeDB\\rules"
    )
    parser.add_argument(
        "--insertData", "-iD",  type=lambda x: (str(x).lower() == 'true'), required=False,
        default = True)
    parser.add_argument(
        "--em_dir_path", "-ed", type=str, required=False,
        help="Absolute path to directory containing EMs"
    )
    parser.add_argument(
        "--insertMetadata", "-iM",  type=lambda x: (str(x).lower() == 'true'), required=False,
        default = True)
    parser.add_argument(
        "--meta_dir", "-md", type=str, required=False,
        help="Directory to metadata", default='.\\Metadata'
    )
    return parser.parse_args()


def main(dbName, defineSchema, schemaFile, defineRules, rulesFile, insertData, em_dir_path, insertMetadata, meta_dir):

    ## inserts data into KG
    migrate_em_json.main(dbName, defineSchema, schemaFile, defineRules, rulesFile, insertData, em_dir_path, insertMetadata, meta_dir)
    ## insert Metadata similarity relationships
    similarityMetadata.main(dbName)
    ## insert Element similarity
    similarityElements.main(dbName)

if __name__ == "__main__":
    main(**vars(parse_args()))