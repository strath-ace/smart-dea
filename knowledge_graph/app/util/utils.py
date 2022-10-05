from typedb.client import *
import re
try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

def typeql_batch_insertion(insertion_query, parameter_list, session, batch_size=128):
    bs = batch_size
    batch_query = []
    counter = 0

    for params_count, params in enumerate(parameter_list):

        # print(params)
        typeql_insert_query = insertion_query.format(**params)
        counter += 1

        if counter < bs and params_count != len(list(parameter_list)) - 1:
            batch_query.append(typeql_insert_query)

        else:

            batch_query.append(typeql_insert_query)
            with session.transaction(TransactionType.WRITE) as transaction:

                for query in batch_query:
                    #print(query)
                    transaction.query().insert(query)
                transaction.commit()
                counter = 0
                batch_query = []

def load_Acronyms(path):
    '''
    load acronyms from .txt file, save acronym and expansion separately
    '''
    # Load acronyms list, manually defined and validated
    acronymsList = []
    path = pathlib.Path(path)
    with open(path, 'r', encoding="utf-8") as inputFile:
        acLine = inputFile.read().split('\n')
        for line in acLine:
            if line:
                acronymsList.append(line.split(' | '))

    acronyms = [x[0] for x in acronymsList]
    #expansions = [word_tokenize(x[1]) for x in acronymsList]
    expansions = [x[1] for x in acronymsList]
    # value "exp" stores preprocessed expansions
  #  exp = []
  #  for item in expansions:
   #     item = ' '.join(item)
    #    #item = item.replace("-", "_")
    #    #item = item.replace(" ", "_")
    #    exp.append(item)

    return acronyms, expansions


def replace_Acronyms(sentence, acronyms, expansions):
    for count, acronym in enumerate(acronyms):
        # if acronym.lower() in sentence.lower():
        # reg = f'\b{acronym.lower}\b'
        if len(acronym) > 1 and not '.' in acronym:
            if re.search(r'\b{}\b'.format(acronym.lower()), sentence.lower()):  # re.search(reg, sentence)
                #print(acronym)

                # sentence = re.sub( f"\s{acronym.lower()}\s", f" {expansions[count]} ",  sentence )
                sentence = re.sub(r'\b{}\b'.format(acronym.lower()), f"{expansions[count]}", sentence.lower())

            elif re.search(r'\b{}s\b'.format(acronym.lower()), sentence.lower()):
                sentence = re.sub(r'\b{}s\b'.format(acronym.lower()), f"{expansions[count]}s", sentence.lower())
                # sentence = re.sub( f"{acronym}s", f"{expansions[count]}s",  sentence )

    return sentence


