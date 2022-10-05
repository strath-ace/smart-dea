# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2022 University of Strathclyde and Author ----------------
# -------------------------------- Author: Paul Darm --------------------------------
# ------------------------- e-mail: paul.darm@strath.ac.uk --------------------------


from typedb.client import *
from tqdm import tqdm
import json
from util.utils import (load_Acronyms, replace_Acronyms, typeql_batch_insertion)
import pandas as pd
import collections
import os
import re
from sentence_transformers import SentenceTransformer, util

def remove_underscore(text):
    return text.replace("_", ' ')


def embed_elements(mappings, acronyms, expansions):
    #script_dir = os.path.dirname(os.path.abspath(__file__))
    #model_dir = os.path.join(script_dir, 'util/all-mpnet-base-v2_local')
    model = SentenceTransformer('all-mpnet-base-v2')

    names = [mapping[0] for mapping in mappings]
    iids = [mapping[1] for mapping in mappings]
    embeds = [model.encode(replace_Acronyms(remove_underscore(name),acronyms,expansions)) for name in tqdm(names)]
    embeds = [str(list(embed)) for embed in embeds]

    return [{'iid': iid, 'embed': embed} for iid, embed in zip(iids, embeds)]

def get_element_names_ids(session):

    """
    :param session: running TypeDB session where data is being migrated
    :return: list of tuples; first element of tuple is the name of the engineering element in KG, second element corresponding respective iid in KG
    """
    with session.transaction(TransactionType.READ) as transaction:
            query = f'''match $ed isa ElementDefinition, has name $nameed;
                     get $ed, $nameed;'''

            iterator = transaction.query().match(query)
            answers = [ans for ans in iterator]
            iids = [ans.get('ed').get_iid() for ans in answers]
            names = [ans.get('nameed').get_value() for ans in answers]

    return [mapping for mapping in zip(names, iids)]

def get_element_ids_embeds(session):
    with session.transaction(TransactionType.READ) as transaction:

        ## Todo change query
        query = '''match $ed isa ElementDefinition, has s_bert_embedding $sbe, has name $nameed;
                     get $ed, $sbe, $nameed;'''

        iterator = transaction.query().match(query)
        answers = [ans for ans in iterator]
        iids = [ans.get('ed').get_iid() for ans in answers]
        elements = [ans.get('nameed').get_value() for ans in answers]
        embeds = [json.loads(ans.get('sbe').get_value()) for ans in answers]

        return {iid:embed for iid, embed in zip(iids, embeds)}

def _del_elements_embeds(session):

        with session.transaction(TransactionType.WRITE) as transaction:

            typeql_delete_query = 'match $ED isa ElementDefinition, has s_bert_embedding $sbe; delete $sbe isa s_bert_embedding;'
            #print(typeql_delete_query)
            transaction.query().delete(typeql_delete_query)
            transaction.commit()


def  _del_elements_sims(session):


    with session.transaction(TransactionType.WRITE) as transaction:

        typeql_delete_query = '''match $ed1 isa ElementDefinition; $ed2 isa ElementDefinition; $refsim(refersTo: $ed1, isReferredBy: $ed2) isa Reference_SimilarityFactor; 
                                     delete $refsim isa Reference_SimilarityFactor;'''

        transaction.query().delete(typeql_delete_query)
        transaction.commit()


def embeddings_insertion(embeding_dic, session):

    insertion_query = '''match $ED iid {iid};      
                           insert $ED has s_bert_embedding "{embed}";'''

    typeql_batch_insertion(insertion_query, embeding_dic, session, batch_size=128)


def calculate_element_sims_name(iids_dicts,session):


    counter = 0
    batch_query = []
    batch = 1024

    #iids = [result[0] for result in results]
    iids = list(iids_dicts.keys())
    print(len(iids))

    ## for index1-th iids in elements
    for index1, iid1 in enumerate(tqdm(iids)):
        ## for all index2-th iids in the subset of elements from index1 to len(element)
        for index2, iid2 in enumerate(iids[index1:]):

            ## skip if comparisons between same element
            if iid1 == iid2:
                continue

            else:

                sim = round(util.pytorch_cos_sim(iids_dicts[iid1], iids_dicts[iid2]).item(), 3)

                typeql_insert_query = f'''match $ed1 iid {iid1};$ed2 iid {iid2}; 
                                 insert (refersTo: $ed1, isReferredBy: $ed2) isa Reference_SimilarityFactor, has simFactor {sim};'''

                ## Todo set parameter in configuration file
                if sim < 0.3:
                    continue

                counter += 1
                if counter < batch:

                    batch_query.append(typeql_insert_query)

                else:
                    print('inserting...')
                    batch_query.append(typeql_insert_query)
                    with session.transaction(TransactionType.WRITE) as transaction:

                        for query in batch_query:
                            transaction.query().insert(query)
                        transaction.commit()
                        counter = 0
                        batch_query = []

    with session.transaction(TransactionType.WRITE) as transaction:
        for query in batch_query:
            transaction.query().insert(query)
        transaction.commit()
        counter = 0


def _del_elements_sims_high_number(session):

        while True:
            offset = 0

            with session.transaction(TransactionType.READ) as transaction:

                typeql_match_query = f'''match $ed1 isa ElementDefinition; $ed2 isa ElementDefinition; $refsim(refersTo: $ed1, isReferredBy: $ed2) isa Reference_SimilarityFactor, has simFactor $sim; get $refsim; offset {offset}; limit 20000;'''

                #                         delete $refsim isa Reference_SimilarityFactor;'''
                iterator = transaction.query().match(typeql_match_query)
                #
                answers = [ans for ans in iterator]
                refsims = [ans.get('refsim').get_iid() for ans in answers]
                print(len(refsims))
            with session.transaction(TransactionType.WRITE) as transaction:
                for refsim in tqdm(refsims):
                    typeql_delete_query = f'match $x iid {refsim}; delete $x isa thing;'

                    # print(typeql_delete_query)
                    transaction.query().delete(typeql_delete_query)

                transaction.commit()

            if len(refsims) < 10000:
                break

def jaccard_weight_similarity(list1,list2, weights):
    comp = list(list1) + list(list2)
    set1 = set(list1)
    set2 = set(list2)
    set_comp = set(comp)
    score = 0
    threshhold = pd.DataFrame.from_dict(weights, orient = 'index').describe().loc['25%'][0]
    b=0
    for param in set1:
        if param in set2:
            score += weights[param]

            if weights[param]>threshhold:
                b=1
    if b:
        return float(score /  sum([weights[param] for param in set_comp]))
    else:
        return 0


def get_ele_paras(namesele, session):
    with session.transaction(TransactionType.READ) as transaction:

        results = {}

        for element in namesele:

            names = []

            query = f'''match $ed isa ElementDefinition, has name $nameed;
                        $nameed = "{element}";                  
                        $it isa Iteration; 
                        $cont1($ed,$it) isa Containment_element; 
                        $te isa ElementDefinition, has name $namete;
                        $reftop($it, $te) isa Reference_topElement;
                        get $namete;'''
            # match $ed isa ElementDefinition, has name "STR Sodern Hydra Electronics Unit";
            iterator = transaction.query().match(query)
            # answers = [ans.get('text') for ans in iterator]
            # lol
            namestopele = [ans.get('namete').get_value() for ans in iterator]
            temp_dic = {}

            for mission in namestopele:

                query = f'''
                    match $ed isa ElementDefinition, has name $nameed;
                    $nameed = "{element}";
                    $cont($ed,$it) isa Containment_element; 
                    $te isa ElementDefinition, has name $namete;
                    $namete = "{mission}";
                    $dom isa DomainOfExpertise, has shortName $DOE;
                    $rel($ed,$dom) isa Reference_owner;
                    $reftop($it, $te) isa Reference_topElement;
                    $para isa Parameter; 
                    $conpara($ed,$para) isa Containment_parameter;
                    $valueset isa ParameterValueSet, has published $publish;
                    $convalue($para, $valueset) isa Containment_valueSet;
                    $paratype isa ParameterType, has name $namept;
                    $refpara($paratype, $para) isa Reference_parameterType;
                    get $namept, $publish, $DOE; offset 0; limit 100;'''

                iterator = transaction.query().match(query)

                names = [ans.get('namept').get_value() for ans in iterator]

                iterator = transaction.query().match(query)
                publish = [ans.get('publish').get_value() for ans in iterator]

                iterator = transaction.query().match(query)
                DOE = [ans.get('DOE').get_value() for ans in iterator]

                if len(names) > 0:
                    ## only parameters where value is not "null"
                    namess = [name for name, para in zip(names, publish) if para != 'null']

                    if len(namess) > 0:
                        namess.append(DOE[0])
                        # namess += [mission]
                        # for key in values_epoch.keys():
                        temp_dic[mission] = namess
                        results[element] = temp_dic

    return results

## ToDo rewrite for batch insertion
def calculate_jaccard_sim(results):

    params = [para for element in results.keys() for mission in results[element].keys() for para in
              results[element][mission]]  # [para for paras in results.values() for para in paras]
    counter_params = collections.Counter(params)

    counter_inv = {param: 1 / counter_params[param] for param in counter_params.keys()}

    ## Combinations for comparing all different Elements

    import itertools
    r = 2
    iterable = list(results.keys())
    combinations = list(itertools.combinations(iterable, r))

    scores_weight = []

    for combination in tqdm(combinations):

        for mission1 in results[combination[0]].keys():

            for mission2 in results[combination[1]].keys():

                scores_weight.append(((combination[0], mission1), (combination[1], mission2),
                                      jaccard_weight_similarity(results[combination[0]][mission1],
                                                                results[combination[1]][mission2], counter_inv)))

    sorted_by_second_weight = sorted(scores_weight, key=lambda tup: tup[2], reverse=True)
    return sorted_by_second_weight

def insert_jaccard_sims(scores, session):
    for score in tqdm(scores):#sorted_by_second_weight:

        if score[2]> 0.1:
            #print('lol')
            with session.transaction(TransactionType.WRITE) as write_transaction:
                # match Iteration of EM with top element called item[0]
                typeql_insert_query = 'match $ed1 isa ElementDefinition, has name "' + score[0][0] + '";'
                typeql_insert_query += f'$te1 isa ElementDefinition, has name "{score[0][1]}";'
                # match Iteration of EM with top element call item[1]


                typeql_insert_query += "$ed2 isa ElementDefinition, has name '" + score[1][0] + "';"
                typeql_insert_query += f'$te2 isa ElementDefinition, has name "{score[1][1]}";'

                typeql_insert_query += '$it1 isa Iteration; $it2 isa Iteration;'
                typeql_insert_query += '$cont1($ed1,$it1) isa Containment_element;'
                typeql_insert_query += '$cont2($ed2,$it2) isa Containment_element;'

                typeql_insert_query += "$reftop1($it1, $te1) isa Reference_topElement;"
                typeql_insert_query += "$reftop2($it2, $te2) isa Reference_topElement;"
                #typeql_insert_query += f'$dom isa DomainOfExpertise, has shortName "{DOE}"; $rel1($ed1,$dom) isa Reference_owner; $rel2($ed2,$dom) isa Reference_owner;'
                #insert relationship to link both
                #typeql_insert_query += "insert $z (refersTo: $it1, isReferredBy: $it2) isa Reference_SimilarityFactor, has simFactor "+ str(item[2]) +" ;"
                typeql_insert_query += "insert $ref_sim(refersTo: $ed1, isReferredBy: $ed2) isa Reference_SimilarityFactor, has simFactorJaccard "+ str(score[2]) +" ;"

                """
                $te isa ElementDefinition, has name $namete;
                $namete = "{mission}";
                $dom isa DomainOfExpertise, has shortName $DOE;
                $rel($ed,$dom) isa Reference_owner;
                $reftop($it, $te) isa Reference_topElement;
                """
                #print(typeql_insert_query)
                write_transaction.query().insert(typeql_insert_query)
                write_transaction.commit()

def main(dbName):

    with TypeDB.core_client('localhost:1729') as client:
        with client.session(dbName, SessionType.DATA) as session:

            ## get all Element definitions from database
            name_iid_mapping = get_element_names_ids(session)
            print(f"{len(name_iid_mapping)} ElementDefinitions found in database.")

            # ## Load Acronym expansion
            script_dir = os.path.dirname(os.path.abspath(__file__))
            #print(script_dir)
            # acronyms_path = pathlib.Path(script_dir,'/util/ecss_acronyms.txt')
            acronyms_path = os.path.join(script_dir, 'util/ecss_acronyms.txt')
            acronyms, expansions = load_Acronyms(acronyms_path)

            # ## Delete old embeddings
            _del_elements_embeds(session)

            # ## Create embeddings for elements names
            embeding_dic = embed_elements(name_iid_mapping,acronyms, expansions)
            assert len(embeding_dic) == len(name_iid_mapping)

            # ## Insert embeddings into database
            embeddings_insertion(embeding_dic,session)

            # ## get embeddings from database
            print("getting embeddings...")
            embed_dic = get_element_ids_embeds(session)
            #
            # ## delete old similarities between elments
            print("deleting previous similarities...")
            # #_del_elements_sims(session)
            # _del_elements_sims_high_number(session)
            print('done!')
            print('calculating and inserting similarities...')
            #
             ## insert similarities between elements
            calculate_element_sims_name(embed_dic, session)
            print('done!')

            # ## Jaccard similarity
            # ## Get elements and parameters
            # print('Getting parameters for each element..  )
            # results = get_ele_paras([name[0] for name in name_iid_mapping], session)
            #
            # ## Calculate similarity scores
            # print('calculating and Jaccard similarities...')
            # scores = calculate_jaccard_sim(results)
            # ## Insert Jaccard similarities
            # print('Inserting and Jaccard similarities...')
            # insert_jaccard_sims(scores, session)


if __name__ == "__main__":

    dbName = "ESAEMs"

    main(dbName)
