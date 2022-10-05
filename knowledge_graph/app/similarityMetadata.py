# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2022 University of Strathclyde and Author ----------------
# -------------------------------- Author: Paul Darm  --------------------------------
# ------------------------- e-mail: paul.darm@strath.ac.uk --------------------------

from typedb.client import *
from tqdm import tqdm
import json
import itertools

from util.utils import (load_Acronyms, replace_Acronyms)

import re
from sentence_transformers import SentenceTransformer, util

def get_metadata_from_KG(mission, session):

    """
    Gets inserted metadata from KG
    :param mission: mission name string, which relates to an Element with that name
    :param session: TypeDB session
    :return:
    """


    temp_metadata = {}
    with session.transaction(TransactionType.READ) as read_transaction:
        typeql_match_query = f'''match $ED isa ElementDefinition,  has name "{mission}";
                                        $metadata isa ParameterGroup, has name "Metadata";
                                        (contains: $ED, isContained: $metadata) isa Containment_parameterGroup;
                                        $parameter isa Parameter, has s_bert_embedding $embed;
                                        (refersTo: $parameter, isReferredBy: $metadata) isa Reference_group;
                                        $parametertype isa SimpleQuantityKind, has name $partypname;
                                        $parametervalueSet isa ParameterValueSet, has published $value;
                                        (contains: $parameter , isContained: $parametervalueSet) isa Containment_valueSet;
                                        (refersTo: $parameter , isReferredBy: $parametertype) isa Reference_parameterType;                                    
                                        get $parameter, $partypname, $value, $embed;'''

        iterator = read_transaction.query().match(typeql_match_query)
        answers = [ans for ans in iterator]

        parameterstypes = [ans.get('partypname').get_value() for ans in answers]

        parameters = [ans.get('parameter').get_iid() for ans in answers]

        values = [ans.get('value').get_value() for ans in answers]
        embeds = [json.loads(ans.get('embed').get_value()) for ans in answers]

        # for parameter, value, embed in zip(parameters, values, embeds):
        for parameterstype, parameter, value, embed in zip(parameterstypes, parameters, values, embeds):

            #                 if parameter =='reference_documents':
            #                       temp_metadata['reference_documents']=  temp_metadata.get('reference_documents', []) +[(value, embed)]
            #                 else:
            #                       temp_metadata[paramete=(value, embed)
            if parameter == 'reference_documents':
                temp_metadata['reference_documents'] = temp_metadata.get('reference_documents', []) + [(parameter, embed)]
            else:
                temp_metadata[parameterstype] = (parameter, value, embed)

        ## Definition of Requirements are linked to RequirementsSpecification entity
        answer_requirements = read_transaction.query().match(
            f"match $eldef isa ElementDefinition, has name '{mission}';"
            # '$meta isa ParameterGroup, has name "Metadata";'
            # "($eldef, $meta) isa Containment_parameterGroup;"
            "$it isa Iteration; ($it, $eldef) isa Reference_topElement;"
            "$reqspec isa RequirementsSpecification, has s_bert_embedding $embed;"
            "(contains:$it, isContained:$reqspec) isa Containment_requirementsSpecification;"
            "$z isa Definition, has content $content;"
            "($reqspec, $z) isa Containment_definition; get $reqspec, $content, $embed;")

        ## Definition of Requirements are linked to Requirements entity
        query2 = (f"match $eldef isa ElementDefinition, has name '{mission}';"
                  # '$meta isa ParameterGroup, has name "Metadata";'
                  # "$eldef isa ElementDefinition; ($eldef, $meta) isa Containment_parameterGroup;"
                  "$it isa Iteration; ($it, $eldef) isa Reference_topElement;"
                  "$reqspec isa RequirementsSpecification, has name $name;"  # optional
                  "(contains:$it, isContained:$reqspec) isa Containment_requirementsSpecification;"
                  "(contains:$metadata, isContained:$reqspec) isa Containment_requirementsSpecification;"
                  "$req isa Requirement, has s_bert_embedding $embed; "  # optional
                  "($reqspec,$req) isa Containment_requirement; "
                  "$z isa Definition, has content $content;"
                  "($req, $z) isa Containment_definition; get $req, $content,$embed, $name;")

        answer_requirements2 = read_transaction.query().match(query2)

        answers1 = [ans for ans in answer_requirements]

        answers2 = [ans for ans in answer_requirements2]

        iids = [ans.get("reqspec").get_iid() for ans in answers1] + [ans.get("req").get_iid() for ans in answers2]

        embeds = [json.loads(ans.get("embed").get_value()) for ans in answers1] + [json.loads(ans.get("embed").get_value())
                                                                                   for ans in answers2]

        # temp_metadata['requirements']=  temp_metadata.get('requirements', []) +[(iids, embeds)]
        temp_metadata['requirements'] = [{'iid': iid, 'encoding': embed} for iid, embed in zip(iids, embeds)]

    return temp_metadata

def compare_meta(model1, model2, metadatas, weight_dict):

    """
    Compares the metadata of two different missions
    :param model1: Mission1 to compare
    :param model2: Mission2 to compare
    :param metadatas: Dict of dicts, which contains the mission names as first keys and metadata names as the second key
    :param weight_dict: dictionary which contains the weighting to calculate the weighted score
    :return: dictionary of scores
    """


    score_dict = {}
    score_dict['models'] = (model1, model2)
    for key in metadatas[model1].keys() - {'reference_documents', 'objectiveCategory'}:
        # print(key)
        if key == 'requirements':
            req_scores = []
            for requirement1 in metadatas[model1]['requirements']:
                max_score = ['str', 'str', 0]
                ## check if comparison requirement <=> req was already added to list of comparisons
                b = 1
                try:
                    for requirement2 in metadatas[model2]['requirements']:
                        # sim = applyDoc2vec(requirement, req, model, ecssMultiwords, stopset)
                        sim = util.pytorch_cos_sim(requirement1['encoding'], requirement2['encoding']).item()
                        if sim > 0.8:
                            req_scores.append([requirement1['iid'], requirement2['iid'], sim])
                            ## set bool to requirement was added to list of comparisons
                            b = 0
                        ## Gets max score == most similar requirement
                        elif sim > max_score[2]:
                            # print(requirement + '\n' + req + '\n'+ 'similarity: '+ str(sim) )
                            # req_scores.append([requirement,req,sim])
                            max_score = [requirement1['iid'], requirement2['iid'], sim]
                    # print(max_score[0] + '\n' + max_score[1] + '\n'+ 'similarity: '+ str(max_score[2]) )
                    ## prevents ZeroDivisionError --> no requirements in engineering model
                    if len(req_scores) == 0:
                        continue
                    ## only add if no requirement was added yet
                    if b:
                        req_scores.append(max_score)

                    sim = sum(score[2] for score in req_scores) / len(req_scores)
                    # print(f'{key}: {sim}, {sim * weight_dict[key]}')
                    score_dict[key] = [sim, req_scores]
                except:
                    continue
            for requirement2 in metadatas[model2]['requirements']:

                if not any([requirement2 == requirement[0] for requirement in req_scores]) and not any(
                        [requirement2 == requirement[1] and 0.9 > requirement[2] for requirement in req_scores]):
                    max_score = ['str', 'str', 0]
                    ## check if comparison requirement <=> req was already added to list of comparisons
                    b = 1
                    try:
                        for requirement1 in metadatas[model1]['requirements']:
                            # sim = applyDoc2vec(requirement, req, model, ecssMultiwords, stopset)
                            sim = util.pytorch_cos_sim(requirement1['encoding'], requirement2['encoding']).item()
                            if sim > 0.8:
                                req_scores.append([requirement1['iid'], requirement2['iid'], sim])
                                ## set bool to requirement was added to list of comparisons
                                b = 0
                            ## Gets max score == most similar requirement
                            elif sim > max_score[2]:
                                # print(requirement + '\n' + req + '\n'+ 'similarity: '+ str(sim) )

                                max_score = [requirement1['iid'], requirement2['iid'], sim]
                        # print(max_score[0] + '\n' + max_score[1] + '\n'+ 'similarity: '+ str(max_score[2]) )
                        if len(req_scores) == 0:
                            continue
                        ## only add if no requirement was added yet
                        if b:
                            req_scores.append(max_score)
                        ## prevents ZeroDivisionError --> no requirements in engineering model

                        sim = sum(score[2] for score in req_scores) / len(req_scores)
                        # print(f'{key}: {sim}, {sim * weight_dict[key]}')
                        score_dict[key] = [sim, req_scores]
                    except:
                        continue
                    # if any([requirement2 == requirement[1] and 0.9>requirement[2]  for requirement in req_scores]):


        elif key == 'launch_date':



            if int(metadatas[model1][key][1]) == int(metadatas[model2][key][1]):

                sim = 1
            else:
                sim = 0

            score_dict[key] = (metadatas[model1][key][0], metadatas[model2][key][0], sim)


        elif key == 'lifetime':


            if float(metadatas[model1][key][1]) == float(metadatas[model2][key][1]):
                sim = 1
            else:
                sim = 0
            score_dict[key] = (metadatas[model1][key][0], metadatas[model2][key][0], sim)


        elif key == 'lagrangePoint':
            if metadatas[model1][key][1] == metadatas[model2][key][1]:
                sim = 1
            else:
                sim = 0

            score_dict[key] = (metadatas[model1][key][0], metadatas[model2][key][0], sim)
        elif key == 'reference_documents':
            ## comparing reference_documents not implemented
            continue

        else:
            score_dict[key] = (metadatas[model1][key][0], metadatas[model2][key][0],
                               util.pytorch_cos_sim(metadatas[model1][key][2], metadatas[model2][key][2]).item())

    score = sum(
        [score_dict[key][0] * weight_dict[key] if key == 'requirements' else score_dict[key][2] * weight_dict[key] for
         key in score_dict.keys() - {'models'}])
    try:
        score = round(score / sum([weight_dict[key] for key in score_dict.keys() - {'models'}]), 3)
    except ZeroDivisionError:
        score = 0
    #      #score / (len(highWParameters) * w[0] + len(mediumWParameter) * w[1] + len(lowWParameter) * w[2]), 3)
    score_dict['total'] = score
    return score_dict

def insert_sims(session, sim):

    """


    :param session: Tyb
    :param sim:
    :return:
    """

    batch_insert_query =[]

    typeql_insert_query = "match $x1 isa ElementDefinition, has name '" + sim['models'][0] +\
                          "'; $it1 isa Iteration; ($it1, $x1) isa Reference_topElement;"
    # match Iteration of EM with top element call item[1]
    typeql_insert_query += "$x2 isa ElementDefinition, has name '" + sim['models'][1] + \
                           "'; $it2 isa Iteration; ($it2, $x2) isa Reference_topElement;"

    # insert relationship to link both
    # typeql_insert_query += "insert $z (refersTo: $it1, isReferredBy: $it2) isa Reference_SimilarityFactor, has simFactor "+ str(item[2]) +" ;"
    typeql_insert_query += 'insert $z (refersTo: $it1, isReferredBy: $it2) isa Reference_SimilarityFactor, has simFactor '+ \
                            str(sim["total"]) + ', has metadataLabel "overall";'

    batch_insert_query.append(typeql_insert_query)

    for key in sim.keys()-{'total', 'models', 'requirements'}:

        typeql_insert_query = f'''match $x iid {sim[key][0]};$y iid {sim[key][1]}; 
                                  insert (refersTo: $x, isReferredBy: $y) isa Reference_SimilarityFactor
                                  , has simFactor {sim[key][2]}, has metadataLabel "{key}";'''

        batch_insert_query.append(typeql_insert_query)

    for combinations in sim.get('requirements', ["",[]])[1]:

        typeql_insert_query = f'''match $x iid {combinations[0]};$y iid {combinations[1]}; 
                                  insert (refersTo: $x, isReferredBy: $y) isa Reference_SimilarityFactor
                                  , has simFactor {combinations[2]}, has metadataLabel "requirement";'''

        batch_insert_query.append(typeql_insert_query)

    with session.transaction(TransactionType.WRITE) as write_transaction:

            for query in batch_insert_query:
                #print(query)

                with open('commits.txt', 'a', encoding='utf-8') as f:
                    f.write(query)
                    f.write('\n')

                write_transaction.query().insert(query)
            write_transaction.commit()

def get_elements_with_metadata(session):

    with session.transaction(TransactionType.READ) as read_transaction:
        typeql_match_query = '''match $ED isa ElementDefinition,  has name $mission;
                                        $metadata isa ParameterGroup, has name "Metadata";
                                        (contains: $ED, isContained: $metadata) isa Containment_parameterGroup;
                                        get $mission;'''

        iterator = read_transaction.query().match(typeql_match_query)
        missions = [ans.get('mission').get_value() for ans in iterator]
        return missions

def delete_previous_sims(session):
    with session.transaction(TransactionType.WRITE) as transaction:

        typeql_delete_query = '''match $para1 isa Parameter; $para2 isa Parameter; $refsim(refersTo: $para1, isReferredBy: $para2) isa Reference_SimilarityFactor;
                                        delete $refsim isa Reference_SimilarityFactor;'''

        transaction.query().delete(typeql_delete_query)
        transaction.commit()

    with session.transaction(TransactionType.WRITE) as transaction:
        typeql_delete_query = '''match $refsim(refersTo: $para1, isReferredBy: $para2) isa Reference_SimilarityFactor, has metadataLabel "requirement";
                                 delete $refsim isa Reference_SimilarityFactor;'''

        transaction.query().delete(typeql_delete_query)
        transaction.commit()



def main(dbName):
    with TypeDB.core_client("localhost:1729") as client:
        with client.session(dbName, SessionType.DATA) as session:

            delete_previous_sims(session)

            missions = get_elements_with_metadata(session)
            print("Following mission with Metadata found in KG" + str(missions))

            print('Getting metadata information...')
            metadatas = {mission: get_metadata_from_KG(mission,session) for mission in missions}

            highW = 0.6
            mediumW = 0.3
            lowW = 0.1

            weight_dict = {'stwDim': lowW, 'propType': mediumW, 'orbitDescription': mediumW, 'lifetime': lowW,
                           'lagrangePoint': lowW, 'background': highW,
                           'missionObjectives': highW, 'orbitType': mediumW, 'reference_documents': lowW,
                           'target': highW, 'plType': mediumW, 'description': highW, 'objectiveCategory': lowW, 'systOfInterest': highW,
                           'launch_date': lowW, 'requirements': highW, 'scienceObjectives': highW, 'objective': highW}

            r = 2
            iterable = list(metadatas.keys())
            combinations = list(itertools.combinations(iterable, r))
            sims =[]

            print('Calculating similarities...')
            for combination in tqdm(combinations):
                sims.append(compare_meta(combination[0], combination[1], metadatas, weight_dict))

            print('Inserting similarities...')
            for sim in tqdm(sims):
                insert_sims(session,sim)


if __name__ == "__main__":

    dbName = "ESAEMs"

    main(dbName)

