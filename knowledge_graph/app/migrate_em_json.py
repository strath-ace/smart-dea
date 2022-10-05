# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2022 University of Strathclyde and Author ----------------
# -------------------------------- Author: Paul Darm / Audrey Berquand --------------------------------
# ------------------------- e-mail: paul.darm@strath.ac.uk --------------------------

'''
This code provides the pipelines for:
- creating a new TypeDB database
- defining the schema layer based on the ECSS-E-TM-10-25A TM
- defining the add-on shema layers for the metadata and the similarity factor
- loading any ECSS-E-TM-10-25A Engineering Models .json export from RHEA CDP4 or OCDT
- inserting Metadata for each EMs's iteration

Pre-requisite:
- TypeDB 2.0.1 installed (https://vaticle.com/),
- TypeDB server running,
- Engineering Models .json files
- Metadata dictionaries
'''

import sys, os
from fnmatch import fnmatch
import ujson as json
import time
import uuid
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib
import logging

from typedb.client import *
from migrationTemplates import *
from collections import Counter
from tqdm import tqdm
from util.utils import (load_Acronyms, replace_Acronyms, typeql_batch_insertion)

from sentence_transformers import SentenceTransformer, util

# --------------------------
# Methods
# --------------------------
def build_engineering_model_graph(em_files, session, Templates):
    """
    Function to insert entities and attributes into a TypeDB database
    :param inputs: .json files containing all data on one Engineering Model
    :param data_path: file path of .json files
    :param session: running TypeDB session where data is being migrated
    :param Templates: function templates used to build the insert queries
    """
    #inputs, data_path
    #Init json file containing all relationships
    init = {'relationship': [], 'role1': [], 'class1': [], 'player1': [], 'role2': [], 'class2': [],
            'player2': []}
    with open('tempRelationships.json', 'w') as file:
        json.dump(init, file)

    # Insert all entities with their attributes, identify entities's roles and relationship partners
    i=0
    for path in em_files:

        tem_path = pathlib.Path(path)
        #input = pathlib.Path(tem_path, input + '.json')
        print("Loading from " + str(tem_path) + " into TypeDB ...")##.json
        load_data_into_typedb(tem_path, session, Templates)
        i=i+1

    # Insert all relationships
    load_relationships_into_typedb(session)

    return

def commitRelationships(session, file):
    '''
    Function to insert relationships in TypeDB session
    :param session: running TypeDB session where data is being migrated
    :param file: .json file storing information on relationships
    '''

    # Load data contained in tempRelationships.json
    with open(file, 'r') as infile:
        input = json.load(infile)
        relationship=input["relationship"]
        role1=input["role1"]
        class1=input["class1"]
        player1=input["player1"]
        role2=input["role2"]
        class2=input["class2"]
        player2=input["player2"]

    #write insert query for each relationship

    counter = 0
    batch = 128
    batch_query = []
    for item_count, idx in enumerate(tqdm(range(len(relationship)))):
        # match player 1
        typeql_insert_query = 'match $player1 isa ' + class1[idx] + ', has id "' + player1[idx] + '";'
        # match player 2
        typeql_insert_query += ' $player2 isa ' + class2[idx] + ', has id "' + player2[idx] + '";'
        # write insert relationship query
        # typeql_insert_query += " insert (" + role1[idx] + ": $player1, " + role2[idx] + ": $player2) isa " + \
        #                        relationship[idx] + ";"
        typeql_insert_query += " insert (" + role1[idx] + ": $player1, " + role2[idx] + ": $player2) isa " + \
                                relationship[idx] +', has rel-id "' +player1[idx]+player2[idx]+'";'
        counter += 1
        if counter < batch and item_count != len(relationship) - 1:
            # batch_query.append(input["template"](item))
            batch_query.append(typeql_insert_query)

        else:
            with session.transaction(TransactionType.WRITE) as transaction:
                # batch_query.append(input["template"](item))
                batch_query.append(typeql_insert_query)
                # print("Executing TypeQL BatchQuery: \n" + "\n".join([query for query in batch_query]))
                for query in batch_query:
                    transaction.query().insert(query)

                # transaction.commit()
                # counter = 0
                # batch_query = []
                ## tries to commit the files, throws error if they are already in the KG (checks unique id for each item)
                try:
                    transaction.commit()
                except TypeDBClientException:
                    transaction.close()
                    for query in batch_query:

                        try:
                            with session.transaction(TransactionType.WRITE) as transaction:
                                transaction.query().insert(query)
                                transaction.commit()
                                print('Inserted Query: ' + query)
                        except:
                            # print('--> Query throws exception:')
                            # print(query)
                            logging.info('Relationship already in Knowledge Graph ' + query)

                counter = 0
                batch_query = []


    return

def load_relationships_into_typedb(session):
    """
    Provides an overview of detected relationships, before inserting them into TypeDB KG
    :param session: running TypeDB session where data is being migrated
    """
    #  Relationships
    with open('tempRelationships.json', 'r') as infile:
        input = json.load(infile)
    print("\n --------------------------------------------------------- ")
    print("Detection of", len(input["relationship"]), "relationships:")
    counter = Counter(input["relationship"])
    for key, value in counter.most_common():
        print(' | ', key, ' | ', value)
    print("Insertion of Relationships: Start...")
    commitRelationships(session, 'tempRelationships.json')
    print("Insertion of Relationships: Success!")

    return

def load_data_into_typedb(input, session, Templates):
    '''
      loads the entities and attributes data into a TypeDB session
      for each item dictionary:
        a. creates a TypeDB transaction
        b. constructs the corresponding TypeQL insert query
        c. runs the query
        d. commits the transaction

      :param input: .json file containing the classes and classes' data to parse and migrate
      :param session: running TypeDB session where data is being migrated
      :param Templates: function templates used to build the insert queries
    '''

    with open(input, 'r', encoding='utf-8') as f:
        items = json.load(f)

    classK=[]
    for item in items:
        classK.append(item["classKind"])

    #Print summary of classes/entities found in .json file, to migrate
    print(f'{len(classK)} Classes to migrate, of {len(list(set(classK)))} different types: {list(set(classK))}')
    listAvailableTemplates = [x for x in Templates.keys()]
    classItems=[]

    # For each item, identify class and call corresponding template from 'migrationTemplates.py'

    #items = json.load(open(input["data_path"] + ".json", encoding='utf-8'))
    ## for each dictionary in items:
    ## a) create a transaction, which closes once used
    ## b) construct the typeql_insert_query using the corresponding template function
    ## c) execute the query and
    ## d) commit the transaction (load in database)
    counter = 0
    batch = 128
    batch_query = []
    for item_count, item in enumerate(tqdm(items)):  ## tqdm added
        """To avoid running out of memory, it’s recommended that every single query gets created and committed in a single transaction. 
        However, for faster migration of large datasets, this can happen once for every n queries, 
        where n is the maximum number of queries guaranteed to run on a single transaction."""
        classItems.append(item["classKind"])
        if item["classKind"] in listAvailableTemplates:
            counter += 1
            if counter < batch and item_count != len(items) - 1:
                #batch_query.append(input["template"](item))
                batch_query.append(Templates[item["classKind"]](item))
            else:
                with session.transaction(TransactionType.WRITE) as transaction:
                    #batch_query.append(input["template"](item))
                    batch_query.append(Templates[item["classKind"]](item))
                    # print("Executing TypeQL BatchQuery: \n" + "\n".join([query for query in batch_query]))
                    for query in batch_query:
                        transaction.query().insert(query.replace('\\', ''))
                    ## tries to commit the files, throws error if they are already in the KG (checks unique id for each item)
                    try:
                        transaction.commit()
                    except TypeDBClientException:
                        transaction.close()
                        for query in batch_query:

                            try:
                                with session.transaction(TransactionType.WRITE) as transaction:
                                     transaction.query().insert(query)
                                     transaction.commit()
                                     print('Inserted Query: ' + query)
                            except:
                                #print('--> Query throws exception:')
                                #print(query)
                                logging.info('Entity already in Knowledge Graph ' + query)



                    counter = 0
                    batch_query = []
        else:
            # if the template for this class has not been found (should not happen)
            print('--> Template for class ', item["classKind"], ' Missing!\n --------------\n ')

    #Print summary
    print("\n --------------------------------------------------------- ")
    #print("\nInserted " + str(len(items)) + " items from [ " + input["file"] + ".json] into TypeDB.\n")

    print("\nInserted " + str(len(items)) + " items from "+ str(input) + "into TypeDB.\n")
    counter = Counter(classItems)
    for key, value in counter.most_common():
        print(' | ', key, ' | ', value)

    return

def check_mission_name(session, mission_name):
        with session.transaction(TransactionType.READ) as transaction:
            typeql_match_query = 'match $ED isa ElementDefinition,  has name "' + mission_name + '"; get $ED;'

            iterator = transaction.query().match(typeql_match_query)
            answers = [ans for ans in iterator]
            answers = [ans.get('ED').get_iid() for ans in answers]
            if len(answers) == 0:
                print(f'Database does not contain mission with name {mission_name}')
                return False
        return True


def check_existing_metadata(session, mission_name):
    with session.transaction(TransactionType.READ) as transaction:
        typeql_match_query = f'''match $ED isa ElementDefinition,  has name "{mission_name}";
                                $metadata isa ParameterGroup, has name "Metadata";
                                (contains: $ED, isContained: $metadata) isa Containment_parameterGroup; get $metadata;'''

        iterator = transaction.query().match(typeql_match_query)
        answers = [ans for ans in iterator]
        answers = [ans.get('metadata').get_iid() for ans in answers]
        if len(answers) > 0:
            print(f'Database already contains metadata for mission with name {mission_name}')
            return False
    return True

def addMetadata(session, mission, model):
    '''
    Function to insert Metadata provided in emList
    :param session: running TypeDB session where data is being migrated
    :param emList: List of metadata dictionaries to be migrated
    '''
    script_dir = os.path.dirname(os.path.abspath(__file__))
    #print(script_dir)
    #acronyms_path = pathlib.Path(script_dir,'/util/ecss_acronyms.txt')
    acronyms_path = os.path.join(script_dir, 'util/ecss_acronyms.txt')
    #print(acronyms_path)
    acronyms, expansions = load_Acronyms(acronyms_path)
    batch_insert_query = []
    assert mission.get(
        'TopElementName') != None, f'Metadata file does not specify mission name  {mission.get("TopElementName")}'
    if check_mission_name(session, mission.get("TopElementName") ) == False:
        return
    if check_existing_metadata(session, mission.get("TopElementName") ) == False:
        return
    typeql_insert_query = 'match $ED isa ElementDefinition,  has name "' + mission['TopElementName'] + '";'
    typeql_insert_query +='insert $metadata isa ParameterGroup, has name "Metadata", has id "' + str(
        uuid.uuid4()) + '";'
    typeql_insert_query += '(contains: $ED, isContained: $metadata) isa Containment_parameterGroup, has rel-id "' + str(
        uuid.uuid4()) + '";'
    # print(typeql_insert_query)



    batch_insert_query.append(typeql_insert_query)

    for meta in mission.keys() - {'TopElementName', 'iteration'}:
        ## special case for requirements --> defined as requirements specification in
        if meta == "requirements":

            typeql_match_query = 'match $ED isa ElementDefinition,  has name "' + mission['TopElementName'] + '";'
            typeql_match_query += '$iteration isa Iteration, has revisionNumber $it;'  # , has name "Metadata";'
            typeql_match_query += '(isReferredBy:$ED, refersTo:$iteration) isa Reference_topElement; get $it; offset 0; limit 100;'
            # typeql_match_query = 'match $iteration isa Iteration, has revisionNumber $x; get $x; offset 0; limit 100;'
            with session.transaction(TransactionType.READ) as transaction:
                iterator = transaction.query().match(typeql_match_query)
                iterations = [int(ans.get('it').get_value()) for ans in iterator]

            assert len(iterations) > 0, f'{mission.get("TopElementName")} does not contain any iterations, needs to be reinserted before adding metadata'
            # if len(iterations)> 1:

            for entry in mission[meta]:
                typeql_insert_query = 'match $ED isa ElementDefinition,  has name "' + mission['TopElementName'] + '";'
                typeql_insert_query += f'$iteration isa Iteration, has revisionNumber "{max(iterations)}";'  # , has name "Metadata";'
                typeql_insert_query += '(isReferredBy:$ED, refersTo:$iteration) isa Reference_topElement;'
                ## insert
                typeql_insert_query += 'insert $reqspec isa RequirementsSpecification, has name "' + entry[
                    'name'] + '", has id "' + str(uuid.uuid4()) + '", has s_bert_embedding "' + str(
                    list(model.encode(replace_Acronyms(entry['name'],acronyms,expansions),show_progress_bar = False))) + '";'
                typeql_insert_query += '(contains:$iteration, isContained:$reqspec) isa Containment_requirementsSpecification, has rel-id "' + str(
                    uuid.uuid4()) + '";'  # +str(uuid.uuid4())+'";'
                typeql_insert_query += '$definition isa Definition, has content "' + entry['definition'] + '", has id "'+str(uuid.uuid4())+'";'
                typeql_insert_query += '(isContained:$definition, contains:$reqspec) isa Containment_definition, has rel-id "' + str(
                    uuid.uuid4()) + '";'
                # print(typeql_insert_query)
                batch_insert_query.append(typeql_insert_query)

        elif type(mission[meta]) == list:
            for entry in mission[meta]:
                typeql_insert_query = 'match $ED isa ElementDefinition,  has name "' + mission['TopElementName'] + '";'
                typeql_insert_query += '$metadata isa ParameterGroup, has name "Metadata";'
                typeql_insert_query += '(contains: $ED, isContained: $metadata) isa Containment_parameterGroup;'
                # typeql_insert_query += 'insert $parameter isa Parameter, has id "'+str(uuid.uuid4())+'";'
                typeql_insert_query += 'insert $parameter isa Parameter, has id "' + str(
                    uuid.uuid4()) + '", has s_bert_embedding "' + str(list(model.encode(entry, show_progress_bar=False))) + '";'

                typeql_insert_query += '$parametertype isa SimpleQuantityKind, has name "' + meta + '", has id "' + str(
                    uuid.uuid4()) + '";'
                typeql_insert_query += '$parametervalueSet isa ParameterValueSet, has published  "' + entry + '", has id "' + str(
                    uuid.uuid4()) + '";'
                # link parameter to metadata group
                typeql_insert_query += '(refersTo: $parameter, isReferredBy: $metadata) isa Reference_group, has rel-id "' + str(
                    uuid.uuid4()) + '";'
                # link parameter to parameter type and value
                typeql_insert_query += '(contains: $parameter , isContained: $parametervalueSet) isa Containment_valueSet, has rel-id "' + str(
                    uuid.uuid4()) + '";'
                typeql_insert_query += '(refersTo: $parameter , isReferredBy: $parametertype) isa Reference_parameterType, has rel-id "' + str(
                    uuid.uuid4()) + '";'
                # print(typeql_insert_query)
                batch_insert_query.append(typeql_insert_query)

        else:
            typeql_insert_query = 'match $ED isa ElementDefinition,  has name "' + mission['TopElementName'] + '";'
            typeql_insert_query += '$metadata isa ParameterGroup, has name "Metadata";'
            typeql_insert_query += '(contains: $ED, isContained: $metadata) isa Containment_parameterGroup;'
            typeql_insert_query += 'insert $parameter isa Parameter, has id "' + str(
                uuid.uuid4()) + '", has s_bert_embedding "' + str(
                list(model.encode(replace_Acronyms(str(mission[meta]),acronyms,expansions)))) + '";'

            typeql_insert_query += '$parametertype isa SimpleQuantityKind, has name "' + meta + '", has id "' + str(
                uuid.uuid4()) + '";'
            typeql_insert_query += '$parametervalueSet isa ParameterValueSet, has published  "' + str(
                mission[meta]) + '", has id "' + str(uuid.uuid4()) + '";'
            # link parameter to metadata group
            typeql_insert_query += '(refersTo: $parameter, isReferredBy: $metadata) isa Reference_group, has rel-id "' + str(
                uuid.uuid4()) + '";'
            # link parameter to parameter type and value
            typeql_insert_query += '(contains: $parameter , isContained: $parametervalueSet) isa Containment_valueSet, has rel-id "' + str(
                uuid.uuid4()) + '";'
            typeql_insert_query += '(refersTo: $parameter , isReferredBy: $parametertype) isa Reference_parameterType, has rel-id "' + str(
                uuid.uuid4()) + '";'

            batch_insert_query.append(typeql_insert_query)

    for query in batch_insert_query:
        # try:

        # with open('commits.txt', 'w+', encoding='utf-8') as f:
        #     f.write(query)
        #     f.write('\n')

        with session.transaction(TransactionType.WRITE) as transaction:
            transaction.query().insert(query)
            transaction.commit()


def load_em_files(em_dir_path):
    """
    Loads .json-files from of EMs from directory
    :param em_dir_path: file path string
    :return: list of dicts containing different EMs jsons
    """

    paths = {}
    pattern = "*.json"
    local_dir = pathlib.Path(em_dir_path)
    for model in local_dir.iterdir():
        ##print(model)
        mission = model.stem
        # print(name)
        temp_paths = []
        for path, subdirs, files in os.walk(model):
            for name in files:
                if fnmatch(name, pattern):
                    if name != 'Header.json' and name != 'Metadata.json':
                        tem_path = pathlib.PurePath(path, name)
                        temp_paths.append(tem_path)

        paths[mission] = temp_paths

    return paths


# --------------------------
# Main
# --------------------------

def main(dbName, defineSchema, schemaFile, defineRules, rule_dir, insertData, em_dir_path, insertMetadata, meta_dir):
    '''
    :param dbName: TypeDB database
    :param defineSchema: If yes, define schema layer based on schemaFile
    :param schemaFile: name of .tql schema file
    :param defineRules: If yes, define additional layers on top of schema based on ruleFiles
    :param rule_dir: directory of schema modifications
    :param insertData: If yes, insert data of Engineering Models listed by emList
    :param em_dir_path: filepath of EMs to load
    :param insertMetadata: If yes, insert Metadata based on emList
    :param meta_dir: Filepath to directory with metadata .jsons
    :return:
    '''

    # Templates functions stored in migrationTemplates.py
    Templates = {"ElementDefinition": elementDefinition_template,
                 "ElementUsage": elementUsage_template,
                 "Parameter": Parameter_template,
                 "ParameterValueSet": ParameterValueSet_template,
                 "Iteration": Iteration_template,
                 "DomainFileStore": domainFileStore_template,
                 "Option": Option_template,
                 "Publication": Publication_template,
                 "ParameterGroup": ParameterGroup_template,
                 "Definition": Definition_template,
                 "ParameterSubscription": ParameterSubscription_template,
                 "ParameterSubscriptionValueSet": ParameterSubscriptionValueSet_template,
                 "RequirementsSpecification": RequirementsSpecification_template,
                 "HyperLink": HyperLink_template,
                 "Category": Category_template,
                 "TextParameterType": TextParameterType_template,
                 "ParameterTypeComponent": ParameterTypeComponent_template,
                 "ReferenceSource": ReferenceSource_template,
                 "BooleanParameterType": BooleanParameterType_template,
                 "BinaryRelationshipRule": BinaryRelationshipRule_template,
                 "Alias": Alias_template,
                 "RatioScale": RatioScale_template,
                 "ArrayParameterType": ArrayParameterType_template,
                 "LinearConversionUnit": LinearConversionUnit_template,
                 "PrefixedUnit": PrefixedUnit_template,
                 "Glossary": Glossary_template,
                 "LogarithmicScale": LogarithmicScale_template,
                 "DerivedUnit": DerivedUnit_template,
                 "ScaleReferenceQuantityValue": ScaleReferenceQuantityValue_template,
                 "UnitFactor": UnitFactor_template,
                 "OrdinalScale": OrdinalScale_template,
                 "DateTimeParameterType": DateTimeParameterType_template,
                 "Term": Term_template,
                 "TimeOfDayParameterType": TimeOfDayParameterType_template,
                 "QuantityKindFactor": QuantityKindFactor_template,
                 "ScaleValueDefinition": ScaleValueDefinition_template,
                 "FileType": FileType_template,
                 "EnumerationParameterType": EnumerationParameterType_template,
                 "UnitPrefix": UnitPrefix_template,
                 "Constant": Constant_template,
                 "DateParameterType": DateParameterType_template,
                 "IntervalScale": IntervalScale_template,
                 "CyclicRatioScale": CyclicRatioScale_template,
                 "EnumerationValueDefinition": EnumerationValueDefinition_template,
                 "Citation": Citation_template,
                 "DecompositionRule": DecompositionRule_template,
                 "CompoundParameterType": CompoundParameterType_template,
                 "MappingToReferenceScale": MappingToReferenceScale_template,
                 "DerivedQuantityKind": DerivedQuantityKind_template,
                 "ParameterizedCategoryRule": ParameterizedCategoryRule_template,
                 "SpecializedQuantityKind": SpecializedQuantityKind_template,
                 "SimpleUnit": SimpleUnit_template,
                 "SimpleQuantityKind": SimpleQuantityKind_template,
                 "SiteDirectory": SiteDirectory_template,
                 "SiteReferenceDataLibrary": SiteReferenceDataLibrary_template,
                 "Person": Person_template,
                 "ModelReferenceDataLibrary": ModelReferenceDataLibrary_template,
                 "EmailAddress": EmailAddress_template,
                 "DomainOfExpertise": DomainOfExpertise_template,
                 "EngineeringModelSetup": EngineeringModelSetup_template,
                 "IterationSetup": IterationSetup_template,
                 "Participant": Participant_template,
                 "EngineeringModel": EngineeringModel_template,
                 "ActualFiniteState": ActualFiniteState_template,
                 "ActualFiniteStateList": ActualFiniteStateList_template,
                 "AndExpression": AndExpression_template,
                 "BinaryRelationship": BinaryRelationship_template,
                 "BooleanExpression": BooleanExpression_template,
                 "BuiltInRuleVerification": BuiltInRuleVerification_template,
                 "CommonFileStore": CommonFileStore_template,
                 "ConversionBasedUnit": ConversionBasedUnit_template,
                 "DefinedThing": DefinedThing_template,
                 "DomainOfExpertiseGroup": DomainOfExpertiseGroup_template,
                 "ElementBase": ElementBase_template,
                 "ExclusiveOrExpression": ExclusiveOrExpression_template,
                 "ExternalIdentifierMap": ExternalIdentifierMap_template,
                 "File": File_template,
                 "FileRevision": FileRevision_template,
                 "FileStore": FileStore_template,
                 "Folder": Folder_template,
                 "IdCorrespondence": IdCorrespondence_template,
                 "MeasurementScale": MeasurementScale_template,
                 "MeasurementUnit": MeasurementUnit_template,
                 "ModelLogEntry": ModelLogEntry_template,
                 "MultiRelationship": MultiRelationship_template,
                 "MultiRelationshipRule": MultiRelationshipRule_template,
                 "NaturalLanguage": NaturalLanguage_template,
                 "NestedElement": NestedElement_template,
                 "NestedParameter": NestedParameter_template,
                 "NotExpression": NotExpression_template,
                 "OrExpression": OrExpression_template,
                 "Organization": Organization_template,
                 "ParameterBase": ParameterBase_template,
                 "ParameterOrOverrideBase": ParameterOrOverrideBase_template,
                 "ParameterOverride": ParameterOverride_template,
                 "ParameterOverrideValueSet": ParameterOverrideValueSet_template,
                 "ParameterType": ParameterType_template,
                 "ParameterValueSetBase": ParameterValueSetBase_template,
                 "ParametricConstraint": ParametricConstraint_template,
                 "ParticipantPermission": ParticipantPermission_template,
                 "ParticipantRole": ParticipantRole_template,
                 "PersonPermission": PersonPermission_template,
                 "PersonRole": PersonRole_template,
                 "PossibleFiniteState": PossibleFiniteState_template,
                 "PossibleFiniteStateList": PossibleFiniteStateList_template,
                 "QuantityKind": QuantityKind_template,
                 "ReferenceDataLibrary": ReferenceDataLibrary_template,
                 "ReferencerRule": ReferencerRule_template,
                 "RelationalExpression": RelationalExpression_template,
                 "Relationship": Relationship_template,
                 "Requirement": Requirement_template,
                 "RequirementsContainer": RequirementsContainer_template,
                 "RequirementsGroup": RequirementsGroup_template,
                 "Rule": Rule_template,
                 "RuleVerification": RuleVerification_template,
                 "RuleVerificationList": RuleVerificationList_template,
                 "RuleViolation": RuleViolation_template,
                 "ScalarParameterType": ScalarParameterType_template,
                 "SimpleParameterValue": SimpleParameterValue_template,
                 "SimpleParameterizableThing": SimpleParameterizableThing_template,
                 "SiteLogEntry": SiteLogEntry_template,
                 "TelephoneNumber": TelephoneNumber_template,
                 "TopContainer": TopContainer_template,
                 "UserPreference": UserPreference_template,
                 "UserRuleVerification": UserRuleVerification_template,
                 "Thing": Thing_template}

    start = time.time()

    print(' \n --> Make sure that your TypeDB server is running  <-- \n')

    with TypeDB.core_client("localhost:1729") as client:

        # check that database exists:
        if not client.databases().contains(dbName):
            client.databases().create(dbName)
            print(f'Database {dbName} created.')
        else:
            print(f'Pre-existing database {dbName} found')

        # ------------------------------------------
        ## open session to write Schema + Rules
        # ------------------------------------------
        with client.session(dbName, SessionType.SCHEMA) as session:

            # Define Schema
            if defineSchema:
                print(f'\nSCHEMA DEFINITION:')
                # read schema.tql
                with open(schemaFile + '.tql', 'r') as inputfile:
                    inputSchema=inputfile.read()

                with session.transaction(TransactionType.WRITE) as write_transaction:
                    write_transaction.query().define(inputSchema)
                    write_transaction.commit()
                print(f'Schema {schemaFile} defined in {dbName}')

            # read query to check nb of concepts in database
            with session.transaction(TransactionType.READ) as read_transaction:
                answer_iterator = read_transaction.query().match("match $x sub thing; get $x; limit 10000;")
                nbConcepts = len([ans.get("x") for ans in answer_iterator])
                read_transaction.concepts()

            if nbConcepts > 4:
                print(f'{nbConcepts} Concepts found in TypeDB Database {dbName}.\n')
            else:
                print(f'Error: Schema not defined.')
                exit()


            # Define rules (if any)
            if defineRules:
                print('\nRULES DEFINITION:')
                rulesFiles = [file for file in pathlib.Path(rule_dir).iterdir()]
                for rule in rulesFiles:
                    #with open(rule + '.tql', 'r') as inputfile:
                    with open(rule, 'r') as inputfile:
                        inputRule = inputfile.read()

                    with session.transaction(TransactionType.WRITE) as write_transaction:
                        write_transaction.query().define(inputRule)
                        write_transaction.commit()
                        print(f'Rules {rule} defined in {dbName}')

            # close session
            pass

        # --------------------------------------------------------
        # Reopen session in DATA mode to insert data and metadata
        # --------------------------------------------------------
        options = TypeDBOptions()
        options.session_idle_timeout_millis= 300_000
        with client.session(dbName, SessionType.DATA, options) as session:
            print(f'\nDATA INSERTION:')
            if insertData:
                listAvailableTemplates = [x for x in Templates.keys()]
                print(len(listAvailableTemplates), ' classes templates available')
                emList = load_em_files(em_dir_path)
                print(emList)
                for mission in emList.keys():

                    print(f'Inserting Engineering Model of the "{mission}" mission')
                    # build_engineering_model_graph(list(em.keys() - {'name'}),
                    #                               [em[key] for key in em.keys() - {'name'}],
                    #                               session, Templates)z
                    build_engineering_model_graph([path for path in emList[mission]],
                                                  session, Templates)


            if insertMetadata:

                print(f'\n METADATA INSERTION:')
                meta_dir = pathlib.Path(meta_dir)
                files = [file for file in meta_dir.iterdir()]
                #script_dir = os.path.dirname(os.path.abspath(__file__))
                #model_dir = os.path.join(script_dir, 'util/all-mpnet-base-v2_local')
                model = SentenceTransformer('all-mpnet-base-v2')

                for file in tqdm(files):

                    if file.suffix == '.json':
                        with file.open('r+', encoding='utf-8-sig') as f:
                            meta = json.load(f)

                        ## connect to client --> typeDB server must be running

                        # with TypeDB.core_client("localhost:1729") as client:
                        #     # Create a database
                        #     with client.session(dbName, SessionType.DATA) as session:
                        addMetadata(session, meta, model)

        pass

    print(f'\nMigration of Schema: {defineSchema}, Rules: {defineRules} and Data: {insertData} done in ',
          round((time.time() - start) / 60, 2), 'minutes.')

    return

if __name__ == "__main__":
    '''
    User Inputs
    Before running main, ensure that the TypeDB server is running! 
    see README.me to learn how to start the server 
    '''

    # Name of TypeDB database to migrate the models to
    dbName = "ESAEMs"#

    # Define graph schema:
    # if True: done via Python API
    # if False: needs to be done via TypeDB console, check Read.me
    # For the data population to work, a schema layer must first be defined!
    defineSchema = False
    schemaFile = '.\\KR_schemas\\TypeDBSchemaECSS_relunique'

    # Define rules (If any)
    # if True: will also define rules
    defineRules = False
    #rulesFile = ['defineMetadata', 'defineSimilarityRelations', 'defineParameternew','defineRequirementnew']
    rulesFile = [".\\KR_schemas\\define_embeddings_similarities"]
    # Insert Data: Populate with Ems
    # if True, will populate the graph with Engineering Models iteration from emList
    insertData = False

    #Insert Metadata: Add on top metadata (in future, hoping that the metadata will already be in the EMs)
    insertMetadata = True

    meta_dir = '.\\Metadata'
    ## create log-file of KG migration

    em_dir_path = "./datasets/"

    '''
    Main
    '''
    main(dbName, defineSchema, schemaFile, defineRules, rulesFile, insertData, em_dir_path, insertMetadata, meta_dir)