# This Source Code Form is subject to the terms of the Mozilla Public ---------------------
# License, v. 2.0. If a copy of the MPL was not distributed with this ---------------------
# file, You can obtain one at http://mozilla.org/MPL/2.0/. */ -----------------------------
# ---------------- Copyright (C) 2020 University of Strathclyde and Author ----------------
# -------------------------------- Author: Audrey Berquand --------------------------------
# ------------------------- e-mail: audrey.berquand@strath.ac.uk --------------------------

'''
This script stores all migrations templates called by migrate_em_json.py,
Each class element from the engineering model migrated to the knowledge graph requires a template:
writing the insert query to insert the migrated class instance's attributes and roles into the graph.
The relationships are committed in bulk after the entities and attributes insertion, they are stored in
tempRelationships.json in the meantime.
Class descriptions found in each template function are extracted from the ECSS-E-TM-10-25A User Manual.
'''

#import json
import ujson as json
# -------------------------------------------------------------
# Methods
# -------------------------------------------------------------

def write_relationship(relation, r1, c1, p1, r2, c2, p2 ):
    '''
    Add new parameters to tempRelationships.json to insert a relationship into Grakn keyspace
    :param relation: relationship name
    :param r1: role 1
    :param c1: class of player 1
    :param p1: player 1 title
    :param r2: role 2
    :param c2: class of player 2
    :param p2: player 2 title
    '''
    assert type(r1) == str
    assert type (c1)== str
    assert type(p1) == str
    assert type(r2) == str
    assert type(c2) == str
    assert type(p2) == str
    with open('tempRelationships.json', 'r') as file:
        data = json.load(file)
    data['relationship'].append(relation)
    data['role1'].append(r1)
    data['player1'].append(p1)
    data['class1'].append(c1)
    data['role2'].append(r2)
    data['class2'].append(c2)
    data['player2'].append(p2)
    with open('tempRelationships.json', 'w') as file:
        json.dump(data, file)

    return

def clean(item):
    '''
    Function to quickly remove special characters from tokens
    :param item: token to "clean"
    :return: cleaned token
    '''

    item=item.replace('\"', '')
    item=item.replace('["-"]', 'null')
    item=item.replace('-', '')
    item = item.replace('"', '')
    item=item.replace('[]', 'null')

    return item

def _template(item):
    '''
    Basic structure for template funtion
    :param item: class element from engineering model
    :return: insert query
    '''
    # class name: class definition
    # the following attributes are basic attributes each class object possesses
    graql_insert_query = 'insert $ isa , has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ";"
    return graql_insert_query

# -------------------------------------------------------------
# 14 Templates for Classes found in Iteration json file
# -------------------------------------------------------------
def elementDefinition_template(item):
    # Element Definition: definition of an element in a design solution for a system-of-interest
    # Insert Attributes
    graql_insert_query = 'insert $element isa ElementDefinition, has name "' + \
                         item["name"] + '", has shortName "' + item["shortName"] + '", has revisionNumber "' + \
                         str(item["revisionNumber"]) +'", has classKind "' + item["classKind"] + '", has id "' + \
                         item["iid"]+ '"'
    graql_insert_query += ";"

    # Collect Relationships
    if item["containedElement"]:
        for i in item["containedElement"]:
            write_relationship('Containment_containedElement', 'contains',
                               'ElementDefinition', item["iid"],'isContained', 'ElementUsage', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'ElementDefinition',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["parameter"]:
        for i in item["parameter"]:
            write_relationship('Containment_parameter', 'contains', 'ElementDefinition',
                               item["iid"], 'isContained', 'Parameter', i)

    if item["parameterGroup"]:
        for i in item["parameterGroup"]:
            write_relationship('Containment_parameterGroup', 'contains', 'ElementDefinition', item["iid"],
                               'isContained', 'ParameterGroup', i)

    if item["referencedElement"]:
        for i in item["referencedElement"]:
            write_relationship('Reference_referencedElement', 'refersTo', 'ElementDefinition', item["iid"],
                               'isReferredBy', 'NestedElement', i)

    if item["owner"]:
        write_relationship('Reference_owner', 'refersTo', 'ElementDefinition', item["iid"],
                           'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ElementDefinition',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ElementDefinition', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ElementDefinition',
                               item["iid"], 'isContained', 'HyperLink', i)

    return graql_insert_query

def elementUsage_template(item):
    # ElementUsage: Named usage of an ElementDefinition in the context of a next higher level ElementDefinition that contains this ElementUsage
    # Insert Attributes
    graql_insert_query = 'insert $elementusage isa ElementUsage, has name "' + \
                         item["name"] + '", has shortName "' + item["shortName"] + '", has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + '", has id "' + item[
                             "iid"] + '", has interfaceEnd "' + item["interfaceEnd"]+\
                          '"'
    graql_insert_query += ";"

    # Collect Relationships
    # An ElementUsage always refers to an ElementDefinition
    write_relationship('Reference_elementDefinition', 'refersTo', 'ElementUsage', item["iid"],
                       'isReferredBy', 'ElementDefinition', item["elementDefinition"])

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'ElementUsage',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["owner"]:
        write_relationship('Reference_owner', 'refersTo', 'ElementUsage', item["iid"],
                           'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ElementUsage',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ElementUsage', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ElementUsage',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["parameterOverride"]:
        for i in item["parameterOverride"]:
            write_relationship('Containment_parameterOverride', 'contains', 'ElementUsage', item["iid"],
                               'isContained', 'ParameterOverride', i)

    if item["excludeOption"]:
        for i in item["excludeOption"]:
            write_relationship('Reference_excludeOption', 'refersTo', 'ElementUsage', item["iid"],
                               'isReferredBy', 'Option ', i)

    return graql_insert_query

def Parameter_template(item):
    # Parameter: representation of a parameter that defines a characteristic or property of an ElementDefinition
    # Insert Attributes
    graql_insert_query = 'insert $parameter isa Parameter, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + '", has id "' + item[
                             "iid"] +  '", has allowDifferentOwnerOfOverride "' + \
                         str(item["allowDifferentOwnerOfOverride"]) + '", has expectsOverride "' + str(item["expectsOverride"]) + \
                         '", has isOptionDependent "' + str(item["isOptionDependent"]) + '"'

    graql_insert_query += ";"

    # Collect Relationships
    if item["owner"]:
        write_relationship('Reference_owner', 'refersTo', 'Parameter', item["iid"],
                           'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["parameterType"]:
        write_relationship('Reference_parameterType', 'refersTo', 'Parameter', item["iid"],
                           'isReferredBy', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refersTo', 'Parameter', item["iid"],
                           'isReferredBy', 'MeasurementScale', item["scale"])

    if item["stateDependence"]:
        write_relationship('Reference_stateDependence', 'refersTo', 'Parameter', item["iid"],
                           'isReferredBy', 'ActualFiniteStateList', item["stateDependence"])

    if item["group"]:
        write_relationship('Reference_group', 'refersTo', 'Parameter', item["iid"],
                           'isReferredBy', 'ParameterGroup', item["group"])

    if item["valueSet"]:
        for i in item["valueSet"]:
            write_relationship('Containment_valueSet', 'contains', 'Parameter', item["iid"],
                               'isContained', 'ParameterValueSet', i)

    if item["requestedBy"]:
        write_relationship('Reference_requestedBy', 'refersTo', 'Parameter', item["iid"],
                           'isReferredBy', 'DomainOfExpertise', item["requestedBy"])

    if item["parameterSubscription"]:
        for i in item["parameterSubscription"]:
            write_relationship('Containment_parameterSubscription', 'contains', 'Parameter', item["iid"],
                               'isContained', 'ParameterSubscription', i)

    return graql_insert_query

def ParameterValueSet_template(item):
    # ParameterValueSet: representation of the switch setting and all values for a Parameter


    graql_insert_query = 'insert $parametervalueset isa ParameterValueSet, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '", has valueSwitch "' + item["valueSwitch"] + '", has published "' + clean(item["published"]) + \
                         '", has formula "' + clean(item["formula"]) + '", has computed "' + clean(item["computed"]) + \
                         '", has manual "' + clean(item["manual"]) + '", has reference "' + clean(item["reference"]) + '"'

    graql_insert_query += ";"

    if item["actualState"]:
        write_relationship('Reference_actualState', 'refersTo', 'ParameterValueSet', item["iid"],
                           'isReferredBy', 'ActualFiniteState', item["actualState"])

    if item["actualOption"]:
        write_relationship('Reference_actualOption', 'refersTo', 'ParameterValueSet', item["iid"],
                           'isReferredBy', 'Option', item["actualOption"])

    return graql_insert_query

def Iteration_template(item):
    #Iteration: representation of an Iteration of an EngineeringModel
    graql_insert_query = 'insert $iteration isa Iteration, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + str(item["iid"]) + '"'
    if item["sourceIterationIid"]:
        graql_insert_query += ', has sourceIterationIid "' + str(item["sourceIterationIid"]) + '"'

    graql_insert_query += ";"

    if item["publication"]:
        for i in item["publication"]:
            write_relationship('Containment_publication', 'contains', 'Iteration', item["iid"],
                           'isContained', 'Publication', i)

    if item["possibleFiniteStateList"]:
        for i in item["possibleFiniteStateList"]:
            write_relationship('Containment_possibleFiniteStateList', 'contains', 'Iteration',
                               item["iid"],'isContained', 'PossibleFiniteStateList', i)

    if item["element"]:
        for i in item["element"]:
            write_relationship('Containment_element', 'contains', 'Iteration',
                               item["iid"],'isContained', 'ElementDefinition', i)

    if item["relationship"]:
        for i in item["relationship"]:
            write_relationship('Containment_relation', 'contains', 'Iteration',
                               item["iid"],'isContained', 'Relationship', i)

    if item["externalIdentifierMap"]:
        for i in item["externalIdentifierMap"]:
            write_relationship('Containment_externalIdentifierMap', 'contains', 'Iteration',
                               item["iid"],'isContained', 'ExternalIdentifierMap', i)

    if item["requirementsSpecification"]:
        for i in item["requirementsSpecification"]:
            write_relationship('Containment_requirementsSpecification', 'contains', 'Iteration',
                               item["iid"],'isContained', 'RequirementsSpecification', i)

    if item["domainFileStore"]:
        for i in item["domainFileStore"]:
            write_relationship('Containment_domainFileStore', 'contains', 'Iteration',
                               item["iid"],'isContained', 'DomainFileStore', i)

    if item["actualFiniteStateList"]:
        for i in item["actualFiniteStateList"]:
            write_relationship('Containment_actualFiniteStateList', 'contains', 'Iteration',
                               item["iid"],'isContained', 'ActualFiniteStateList', i)

    if item["ruleVerificationList"]:
        for i in item["ruleVerificationList"]:
            write_relationship('Containment_ruleVerificationList', 'contains', 'Iteration',
                               item["iid"], 'isContained', 'RuleVerificationList', i)

    if item["iterationSetup"]:
        write_relationship('Reference_iterationSetup', 'refersTo', 'Iteration',
                               item["iid"], 'isReferredBy', 'IterationSetup', item["iterationSetup"])

    if item["topElement"]:
        write_relationship('Reference_topElement', 'refersTo', 'Iteration',
                           item["iid"], 'isReferredBy', 'ElementDefinition', item["topElement"])

    if item["defaultOption"]:
        write_relationship('Reference_defaultOption', 'refersTo', 'Iteration',
                           item["iid"], 'isReferredBy', 'Option', item["defaultOption"])

    if item["option"]:
        for i in item["option"]:
            write_relationship('Containment_option', 'contains', 'Iteration',
                               item["iid"], 'isContained', 'Option', i["v"])

    return graql_insert_query

def domainFileStore_template(item):
    # domainFileStore= domain specific FileStore for use by single DomainOfExpertise

    graql_insert_query = 'insert $domainfilestore isa DomainFileStore, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'

    graql_insert_query += ', has isHidden "' + str(item["isHidden"]) + '", has name "' + item["name"] + '", has createdOn "' + str(item["createdOn"]) + '"'

    graql_insert_query += ";"

    if item["owner"]:
        write_relationship('Reference_owner', 'refersTo', 'DomainFileStore', item["iid"],
                           'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["folder"]:
        for i in item["folder"]:
            write_relationship('Containment_folder', 'contains', 'DomainFileStore', item["iid"],
                               'isContained', 'Folder', i)

    if item["file"]:
        for i in item["file"]:
            write_relationship('Containment_file', 'contains', 'DomainFileStore', item["iid"],
                               'isContained','File', i)

    return graql_insert_query

def Option_template(item):
    # Option: representation of an option that is a potential design solution for the system-of-interest
    # being developed in an Iteration of an EngineeringModel

    graql_insert_query = 'insert $option isa Option, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'

    graql_insert_query += ', has name "' + item["name"] + '", has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"


    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'Option',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'Option', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'Option',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'Option',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["nestedElement"]:
        for i in item["nestedElement"]:
            write_relationship('Containment_nestedElement', 'contains', 'Option',
                               item["iid"], 'isContained', 'NestedElement', i)
    return graql_insert_query

def Publication_template(item):
    #Publication: representation of a saved state within an Iteration where all computed values of the
    # ParameterValueSets of a selected set of Parameters and ParameterOverrides are published to (i.e. copied to)
    # the published values

    graql_insert_query = 'insert $publication isa Publication, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'

    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ";"

    if item["domain"]:
        for i in item["domain"]:
            write_relationship('Reference_domain', 'refersTo', 'Publication',
                               item["iid"], 'isReferredBy', 'DomainOfExpertise', i)

    if item["publishedParameter"]:
        for i in item["publishedParameter"]:
            write_relationship('Reference_publishedParameter', 'refersTo', 'Publication',
                               item["iid"], 'isReferredBy', 'ParameterOrOverrideBase', i)

    return graql_insert_query

def ParameterGroup_template(item):
    #ParameterGroup: representation of a group of Parameters within an ElementDefinition

    graql_insert_query = 'insert $parameterGroup isa ParameterGroup, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'

    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ";"

    if item["containingGroup"]:
        write_relationship('Reference_containingGroup', 'refersTo', 'ParameterGroup',
                           item["iid"], 'isReferredBy', 'ParameterOrOverrideBase', item["containingGroup"])

    return graql_insert_query

def Definition_template(item):
    #Definition: representation of a textual definition in a given natural language
    graql_insert_query = 'insert $definition isa Definition, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'

    graql_insert_query += ', has languageCode "' + item["languageCode"] + '"'
    graql_insert_query += ', has content "' + clean(item["content"]) + '"'

    if item["note"]:
        # Combine all notes into 1 as Grakn only accepts one instance of one attribute
        combinedNotes=''
        for i in item["note"]:
            combinedNotes += clean(i["v"])+ ' ,'
        graql_insert_query += ', has note "' + combinedNotes + '"'

    if item["example"]:
        # Combine all notes into 1
        combinedEx=''
        for i in item["example"]:
            combinedEx += i["v"] + ' ,'
        graql_insert_query += ', has example "' + combinedEx + '"'

    graql_insert_query += ";"

    if item["citation"]:
        for i in item["citation"]:
            write_relationship('Containment_citation', 'contains', 'Definition',
                               item["iid"], 'isContained', 'Citation', i)

    return graql_insert_query

def ParameterSubscription_template(item):
    # ParameterSubscription: representation of a subscription to a Parameter or ParameterOverride taken by
    # a DomainOfExpertise that is not the owner of the Parameter or ParameterOverride
    graql_insert_query = 'insert $parametersubscription isa ParameterSubscription, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'

    graql_insert_query += ";"

    if item["owner"]:
        write_relationship('Reference_owner', 'refersTo', 'ParameterSubscription', item["iid"],
                           'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["valueSet"]:
        for i in item["valueSet"]:
            write_relationship('Containment_valueSet', 'contains', 'ParameterSubscription', item["iid"],
                               'isContained', 'ParameterValueSet', i)
    return graql_insert_query

def ParameterSubscriptionValueSet_template(item):
    # ParameterSubscriptionValueSet: representation of the switch setting and all values of a ParameterSubscription
    graql_insert_query = 'insert $parametersubscriptionvalueset isa ParameterSubscriptionValueSet, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'
    ## ToDo
    graql_insert_query += ', has valueSwitch "' + item["valueSwitch"] + '"'
    #graql_insert_query += ', has computed "' + item["computed"] + '"'
    graql_insert_query += ', has manual "' + clean(item["manual"]) + '"'
    #graql_insert_query += ', has reference "' + item["reference"] + '"'
    #graql_insert_query += ', has actualValue "' + item["actualValue"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

def RequirementsSpecification_template(item):
    # RequirementsSpecification: representation of a requirements specification
    graql_insert_query = 'insert $requirementsspecification isa RequirementsSpecification, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'

    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'RequirementsSpecification',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'RequirementsSpecification', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'RequirementsSpecification',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["group"]:
        for i in item["group"]:
            write_relationship('Reference_group', 'refersTo', 'RequirementsSpecification', item["iid"],
                               'isReferredBy', 'ParameterGroup', i)

    if item["owner"]:
        write_relationship('Reference_owner', 'refersTo', 'RequirementsSpecification', item["iid"],
                           'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["requirement"]:
        for i in item["requirement"]:
            write_relationship('Containment_requirement', 'contains', 'RequirementsSpecification',
                               item["iid"], 'isContained', 'Requirement', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'RequirementsSpecification',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["parameterValue"]:
        for i in item["parameterValue"]:
            write_relationship('Containment_valueSet', 'contains', 'RequirementsSpecification', item["iid"],
                               'isContained', 'ParameterValueSet', i)

    return graql_insert_query

def HyperLink_template(item):
    # Hyperlink: representation of a hyperlink consisting of a URI and a descriptive text
    graql_insert_query = 'insert $hyperLink isa HyperLink, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'

    graql_insert_query += ', has uri "' + item["uri"] + '"'
    graql_insert_query += ', has languageCode "' + item["languageCode"] + '"'
    graql_insert_query += ', has content "' + item["content"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

# -------------------------------------------------------------
# 39 Templates for Classes found in SiteReferenceDataLibraries json file
# -------------------------------------------------------------
def Category_template(item):
    # Category: representation of a user-defined category for categorization of instances that have common characteristics
    graql_insert_query = 'insert $category isa Category, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'

    if item["isAbstract"]:
        graql_insert_query += ', has isAbstract "' + str(item["isAbstract"]) + '"'

    if item["isDeprecated"]:
        graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'

    if item["permissibleClass"]:
        combinedPermissibleClass = ''
        for i in item["permissibleClass"]:
            combinedPermissibleClass += i + ' ,'
        graql_insert_query += ', has permissibleClass "' + combinedPermissibleClass + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'Category',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'Category', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'Category',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["superCategory"]:
        for i in item["superCategory"]:
            write_relationship('Reference_superCategory', 'refersTo', 'Category',
                               item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def Alias_template(item):
    # Alias: representation of an alternative human-readable name for a concept
    graql_insert_query = 'insert $alias isa Alias, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'

    graql_insert_query += ', has isSynonym "' + str(item["isSynonym"]) + '"'
    graql_insert_query += ', has languageCode "' + item["languageCode"] + '"'
    graql_insert_query += ', has content "' + item["content"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

def Term_template(item):
    # Term: definition of a term in a Glossary of terms
    graql_insert_query = 'insert $term isa Term , has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'Term',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'Term', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'Term',
                               item["iid"], 'isContained', 'HyperLink', i)

    return graql_insert_query

def Citation_template(item):
    # Citation: reference with cited location to a ReferenceSource
    graql_insert_query = 'insert $citation isa Citation , has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'

    if item["location"]:
        graql_insert_query += ', has location "' + item["location"] + '"'

    if item["remark"]:
        graql_insert_query += ', has remark "' + item["remark"] + '"'

    graql_insert_query += ', has isAdaptation "' + str(item["isAdaptation"]) + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_source', 'refersTo', 'Citation',
                       item["iid"], 'isReferredBy', 'ReferenceSource', item["source"])

    return graql_insert_query

def QuantityKindFactor_template(item):
    # QuantityKindFactor: representation of a QuantityKind and an exponent that together define one factor in a product
    # of powers of QuantityKinds

    graql_insert_query = 'insert $quantitykindfactor isa QuantityKindFactor, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'

    if item["exponent"]:
        graql_insert_query += ', has exponent "' + item["exponent"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_quantityKind', 'refersTo', 'QuantityKindFactor',
                       item["iid"], 'isReferredBy', 'QuantityKind', item["quantityKind"])

    return graql_insert_query

def CyclicRatioScale_template(item):
    # CyclicRatioScale: representation of a ratio MeasurementScale with a periodic cycle
    graql_insert_query = 'insert $cyclicratioscale isa CyclicRatioScale, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has modulus "' + item["modulus"] + '"'
    graql_insert_query += ', has numberSet "' + item["numberSet"] + '"'
    graql_insert_query += ', has isMinimumInclusive "' + str(item["isMinimumInclusive"]) + '"'
    graql_insert_query += ', has isMaximumInclusive "' + str(item["isMaximumInclusive"]) + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'

    if item["minimumPermissibleValue"]:
        graql_insert_query += ', has minimumPermissibleValue "' + item["minimumPermissibleValue"] + '"'
    if item["maximumPermissibleValue"]:
       graql_insert_query += ', has maximumPermissibleValue "' + item["maximumPermissibleValue"] + '"'
    if item["positiveValueConnotation"]:
        graql_insert_query += ', has positiveValueConnotation "' + item["positiveValueConnotation"] + '"'
    if item["negativeValueConnotation"]:
        graql_insert_query += ', has negativeValueConnotation "' + item["negativeValueConnotation"] + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'CyclicRatioScale',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'CyclicRatioScale', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'CyclicRatioScale',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["valueDefinition"]:
        for i in item["valueDefinition"]:
            write_relationship('Containment_valueDefinition', 'contains', 'CyclicRatioScale',
                               item["iid"], 'isContained', 'ScaleValueDefinition', i)

    if item["mappingToReferenceScale"]:
        for i in item["mappingToReferenceScale"]:
            write_relationship('Containment_mappingToReferenceScale', 'contains', 'CyclicRatioScale',
                               item["iid"], 'isContained', 'MappingToReferenceScale', i)

    write_relationship('Reference_unit', 'refersTo', 'CyclicRatioScale',
                       item["iid"], 'isReferredBy', 'MeasurementUnit', item["unit"])

    return graql_insert_query

def PrefixedUnit_template(item):
    # PrefixedUnit: specialization of ConversionBasedUnit that defines a MeasurementUnit with
    # a multiple or submultiple UnitPrefix
    graql_insert_query = 'insert $prefixedunit isa PrefixedUnit, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'PrefixedUnit',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'PrefixedUnit', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'PrefixedUnit',
                               item["iid"], 'isContained', 'HyperLink', i)

    write_relationship('Reference_referenceUnit', 'refersTo', 'PrefixedUnit',
                       item["iid"], 'isReferredBy', 'MeasurementUnit', item["referenceUnit"])

    write_relationship('Reference_prefix', 'refersTo', 'PrefixedUnit',
                       item["iid"], 'isReferredBy', 'UnitPrefix', item["prefix"])

    return graql_insert_query

def DecompositionRule_template(item):
    # DecompositionRule : representation of a validation rule for system-of-interest decomposition through
    # containingElement ElementDefinitions and containedElement ElementUsages
    graql_insert_query = 'insert $decompositionrule isa DecompositionRule, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has minContained "' + str(item["minContained"]) +'"'

    if item["maxContained"]:
        graql_insert_query += ', has maxContained ' + str(item["maxContained"])

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'DecompositionRule',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'DecompositionRule', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'DecompositionRule',
                               item["iid"], 'isContained', 'HyperLink', i)

    write_relationship('Reference_containingCategory', 'refersTo', 'DecompositionRule',
                       item["iid"], 'isReferredBy', 'Category', item["containingCategory"])

    if item["containedCategory"]:
        for i in item["containedCategory"]:
            write_relationship('Reference_containedCategory', 'refersTo', 'DecompositionRule',
                               item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def RatioScale_template(item):
    # RatioScale: kind of MeasurementScale that has ordered values, a measurement unit and a fixed definition of
    # the zero value on all scales for the same kind of quantity
    graql_insert_query = 'insert $ratioscale isa RatioScale, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '"'

    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has numberSet "' + item["numberSet"] + '"'
    graql_insert_query += ', has isMinimumInclusive "' + str(item["isMinimumInclusive"]) + '"'
    graql_insert_query += ', has isMaximumInclusive "' + str(item["isMaximumInclusive"]) + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    if item["minimumPermissibleValue"]:
        graql_insert_query += ', has minimumPermissibleValue "' + item["minimumPermissibleValue"] + '"'
    if item["maximumPermissibleValue"]:
        graql_insert_query += ', has maximumPermissibleValue "' + item["maximumPermissibleValue"] + '"'
    if item["positiveValueConnotation"]:
        graql_insert_query += ', has positiveValueConnotation "' + item["positiveValueConnotation"] + '"'
    if item["negativeValueConnotation"]:
        graql_insert_query += ', has negativeValueConnotation "' + item["negativeValueConnotation"] + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'RatioScale',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'RatioScale', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'RatioScale',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["valueDefinition"]:
        for i in item["valueDefinition"]:
            write_relationship('Containment_valueDefinition', 'contains', 'RatioScale',
                               item["iid"], 'isContained', 'ScaleValueDefinition', i)

    if item["mappingToReferenceScale"]:
        for i in item["mappingToReferenceScale"]:
            write_relationship('Containment_mappingToReferenceScale', 'contains', 'RatioScale',
                               item["iid"], 'isContained', 'MappingToReferenceScale', i)

    write_relationship('Reference_unit', 'refersTo', 'RatioScale',
                       item["iid"], 'isReferredBy', 'MeasurementUnit', item["unit"])

    return graql_insert_query

def FileType_template(item):
    # FileType: representation of the type of a File
    graql_insert_query = 'insert $filetype isa FileType, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has extension "' + item["extension"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'FileType',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'FileType', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'FileType',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'FileType',
                               item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def SimpleQuantityKind_template(item):
    # SimpleQuantityKind: specialization of QuantityKind that represents a kind of quantity that
    # does not depend on any other QuantityKind
    graql_insert_query = 'insert $simplequantitykind isa SimpleQuantityKind, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'

    if item["quantityDimensionSymbol"]:
        graql_insert_query += ', has quantityDimensionSymbol "' + item["quantityDimensionSymbol"] + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'SimpleQuantityKind',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'SimpleQuantityKind', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'SimpleQuantityKind',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'SimpleQuantityKind',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["possibleScale"]:
        for i in item["possibleScale"]:
            write_relationship('Reference_possibleScale', 'refersTo', 'SimpleQuantityKind',
                               item["iid"], 'isReferredBy', 'MeasurementScale', i)

    if item["defaultScale"]:
        write_relationship('Reference_defaultScale', 'refersTo', 'SimpleQuantityKind',
                               item["iid"], 'isReferredBy', 'MeasurementScale', item["defaultScale"])

    return graql_insert_query

def TextParameterType_template(item):
    # TextParameterType: representation of a character string valued ScalarParameterType
    graql_insert_query = 'insert $textparametertype isa TextParameterType, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'TextParameterType',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'TextParameterType', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'TextParameterType',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'TextParameterType',
                               item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def LogarithmicScale_template(item):
    # LogarithmicScale: representation of a logarithmic MeasurementScale
    graql_insert_query = 'insert $logarithmicscale isa LogarithmicScale, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has numberSet "' + item["numberSet"] + '"'
    graql_insert_query += ', has isMinimumInclusive "' + str(item["isMinimumInclusive"]) + '"'
    graql_insert_query += ', has isMaximumInclusive "' + str(item["isMaximumInclusive"]) + '"'
    graql_insert_query += ', has logarithmBase "' + item["logarithmBase"] + '"'
    graql_insert_query += ', has factor "' + item["factor"] + '"'
    graql_insert_query += ', has exponent "' + item["exponent"] + '"'
    if item["minimumPermissibleValue"]:
        graql_insert_query += ', has minimumPermissibleValue "' + item["minimumPermissibleValue"] + '"'
    if item["maximumPermissibleValue"]:
        graql_insert_query += ', has maximumPermissibleValue "' + item["maximumPermissibleValue"] + '"'
    if item["positiveValueConnotation"]:
        graql_insert_query += ', has positiveValueConnotation "' + item["positiveValueConnotation"] + '"'
    if item["negativeValueConnotation"]:
        graql_insert_query += ', has negativeValueConnotation "' + item["negativeValueConnotation"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'LogarithmicScale',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'LogarithmicScale', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'LogarithmicScale',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["valueDefinition"]:
        for i in item["valueDefinition"]:
            write_relationship('Containment_valueDefinition', 'contains', 'LogarithmicScale',
                               item["iid"], 'isContained', 'ScaleValueDefinition', i)

    if item["mappingToReferenceScale"]:
        for i in item["mappingToReferenceScale"]:
            write_relationship('Containment_mappingToReferenceScale', 'contains', 'LogarithmicScale',
                               item["iid"], 'isContained', 'MappingToReferenceScale', i)

    write_relationship('Reference_unit', 'refersTo', 'RatioScale',
                       item["iid"], 'isReferredBy', 'MeasurementUnit', item["unit"])

    if item["referenceQuantityValue"]:
        for i in item["referenceQuantityValue"]:
           write_relationship('Containment_referenceQuantityValue', 'contains', 'LogarithmicScale',
                                   item["iid"], 'isContained', 'ScaleReferenceQuantityValue', i)


    write_relationship('Reference_referenceQuantityKind', 'refersTo', 'LogarithmicScale',
                               item["iid"], 'isReferredBy', 'QuantityKind', item["referenceQuantityKind"])

    return graql_insert_query

def EnumerationValueDefinition_template(item):
    # EnumerationValueDefinition: representation of one enumeration value of an EnumerationParameterType
    graql_insert_query = 'insert $enumerationvaluedefinition isa EnumerationValueDefinition, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'EnumerationValueDefinition',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'EnumerationValueDefinition', item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'EnumerationValueDefinition',
                               item["iid"], 'isContained', 'HyperLink', i)
    return graql_insert_query

def ParameterTypeComponent_template(item):
    # ParameterTypeComponent: representation of a component of a CompoundParameterType
    graql_insert_query = 'insert $parametertypecomponent isa ParameterTypeComponent, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_parameterType', 'refersTo', 'ParameterTypeComponent', item["iid"],
                           'isReferredBy', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refersTo', 'ParameterTypeComponent', item["iid"],
                           'isReferredBy', 'MeasurementScale', item["scale"])

    return graql_insert_query

def ScaleReferenceQuantityValue_template(item):
    # ScaleReferenceQuantityValue: representation of a reference quantity with value for the definition of
    # logarithmic MeasurementScales
    graql_insert_query = 'insert $scalereferencequantityvalue isa ScaleReferenceQuantityValue, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has value "' + clean(item["value"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_scale', 'refersTo', 'ScaleReferenceQuantityValue', item["iid"],
                           'isReferredBy', 'MeasurementScale', item["scale"])

    return graql_insert_query

def MappingToReferenceScale_template(item):
    # MappingToReferenceScale: representation of a mapping of a value on a dependent MeasurementScale to a value on a
    # reference MeasurementScale that represents the same quantity
    graql_insert_query = 'insert $mappingtoreferencescale isa MappingToReferenceScale, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'

    graql_insert_query += ";"

    write_relationship('Reference_referenceScaleValue', 'refersTo', 'MappingToReferenceScale', item["iid"],
                       'isReferredBy', 'ScaleValueDefinition', item["referenceScaleValue"])

    write_relationship('Reference_dependentScaleValue', 'refersTo', 'MappingToReferenceScale', item["iid"],
                       'isReferredBy', 'ScaleValueDefinition', item["dependentScaleValue"])

    return graql_insert_query

def BinaryRelationshipRule_template(item):
    # BinaryRelationshipRule: representation of a validation rule for BinaryRelationships
    graql_insert_query = 'insert $binaryrelationshiprule isa BinaryRelationshipRule, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'

    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has forwardRelationshipName "' + item["forwardRelationshipName"] + '"'
    graql_insert_query += ', has inverseRelationshipName "' + item["inverseRelationshipName"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'BinaryRelationshipRule',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'BinaryRelationshipRule',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'BinaryRelationshipRule',
                               item["iid"], 'isContained', 'HyperLink', i)

    write_relationship('Reference_relationshipCategory', 'refersTo', 'BinaryRelationshipRule',
                       item["iid"], 'isReferredBy', 'Category', item["relationshipCategory"])

    write_relationship('Reference_sourceCategory', 'refersTo', 'BinaryRelationshipRule',
                       item["iid"], 'isReferredBy', 'Category', item["sourceCategory"])

    write_relationship('Reference_targetCategory', 'refersTo', 'BinaryRelationshipRule',
                       item["iid"], 'isReferredBy', 'Category', item["targetCategory"])

    return graql_insert_query

def UnitFactor_template(item):
    # UnitFactor: representation of a factor in the product of powers that defines a DerivedUnit
    graql_insert_query = 'insert $unitfactor isa UnitFactor, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has exponent "' + item["exponent"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_unit', 'refersTo', 'UnitFactor',
                       item["iid"], 'isReferredBy', 'MeasurementUnit', item["unit"])

    return graql_insert_query

def ReferenceSource_template(item):
    # ReferenceSource: representation of an information source that can be referenced
    graql_insert_query = 'insert $referencesource isa ReferenceSource, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'

    if item["versionIdentifier"]:
        graql_insert_query += ', has versionIdentifier "' + item["versionIdentifier"] + '"'

    if item["versionDate"]:
        graql_insert_query += ', has versionDate "' + item["versionDate"] + '"'

    if item["author"]:
        graql_insert_query += ', has author "' + item["author"] + '"'

    if item["publicationYear"]:
        graql_insert_query += ', has publicationYear "' + str(item["publicationYear"]) +'"'

    if item["language"]:
        graql_insert_query += ', has language "' + item["language"] + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ReferenceSource',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ReferenceSource',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ReferenceSource',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'ReferenceSource',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["publisher"]:
        write_relationship('Reference_publisher', 'refersTo', 'ReferenceSource',
                               item["iid"], 'isReferredBy', 'Organization', item["publisher"])

    if item["publishedIn"]:
        write_relationship('Reference_publishedIn', 'refersTo', 'ReferenceSource',
                               item["iid"], 'isReferredBy', 'ReferenceSource', item["publishedIn"])

    return graql_insert_query

def Constant_template(item):
    # Constant: representation of a named constant, typically a mathematical or physical constant
    graql_insert_query = 'insert $constant isa Constant, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has value "' + clean(item["value"]) + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'Constant',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'Constant',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'Constant',
                               item["iid"], 'isContained', 'HyperLink', i)

    write_relationship('Reference_parameterType', 'refersTo', 'Constant', item["iid"],
                               'isReferredBy', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refersTo', 'Constant', item["iid"],
                       'isReferredBy', 'MeasurementScale', item["scale"])

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'Constant',
                               item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def IntervalScale_template(item):
    # IntervalScale: kind of MeasurementScale that has ordered values, a measurement unit and an arbitrary zero value
    graql_insert_query = 'insert $intervalscale isa IntervalScale, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has numberSet "' + item["numberSet"] + '"'
    graql_insert_query += ', has isMinimumInclusive "' + str(item["isMinimumInclusive"]) + '"'
    graql_insert_query += ', has isMaximumInclusive "' + str(item["isMaximumInclusive"]) + '"'
    if item["minimumPermissibleValue"]:
        graql_insert_query += ', has minimumPermissibleValue "' + item["minimumPermissibleValue"] + '"'
    if item["maximumPermissibleValue"]:
        graql_insert_query += ', has maximumPermissibleValue "' + item["maximumPermissibleValue"] + '"'
    if item["positiveValueConnotation"]:
        graql_insert_query += ', has positiveValueConnotation "' + item["positiveValueConnotation"] + '"'
    if item["negativeValueConnotation"]:
        graql_insert_query += ', has negativeValueConnotation "' + item["negativeValueConnotation"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'IntervalScale',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'IntervalScale',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'IntervalScale',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["valueDefinition"]:
        for i in item["valueDefinition"]:
            write_relationship('Containment_valueDefinition', 'contains', 'IntervalScale',
                               item["iid"], 'isContained', 'ScaleValueDefinition', i)

    if item["mappingToReferenceScale"]:
        for i in item["mappingToReferenceScale"]:
            write_relationship('Containment_mappingToReferenceScale', 'contains', 'IntervalScale',
                               item["iid"], 'isContained', 'MappingToReferenceScale', i)

    write_relationship('Reference_unit', 'refersTo', 'IntervalScale',
                       item["iid"], 'isReferredBy', 'MeasurementUnit', item["unit"])

    return graql_insert_query

def DerivedQuantityKind_template(item):
    # DerivedQuantityKind: specialization of QuantityKind that represents a kind of quantity that is defined as a
    # product of powers of one or more other kinds of quantity
    graql_insert_query = 'insert $derivedquantitykind isa DerivedQuantityKind, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    if item["quantityDimensionSymbol"]:
        graql_insert_query += ', has quantityDimensionSymbol "' + item["quantityDimensionSymbol"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'DerivedQuantityKind',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'DerivedQuantityKind',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'DerivedQuantityKind',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'DerivedQuantityKind',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["quantityKindFactor"]:
        for i in item["quantityKindFactor"]:
            write_relationship('Containment_quantityKindFactor', 'contains', 'DerivedQuantityKind',
                               item["iid"], 'isContained', 'QuantityKindFactor', i["v"])

    if item["possibleScale"]:
        for i in item["possibleScale"]:
            write_relationship('Reference_possibleScale', 'refersTo', 'DerivedQuantityKind',
                               item["iid"], 'isReferredBy', 'MeasurementScale', i)

    write_relationship('Reference_defaultScale', 'refersTo', 'DerivedQuantityKind',
                       item["iid"], 'isReferredBy', 'MeasurementScale', item["defaultScale"])

    #ToDo
    '''
    # Not found in json file:
    has quantityDimensionExpression,  
    has quantityDimensionExponent, 
    has numberOfValues,  
    plays refers_allPossibleScale,
    '''

    return graql_insert_query

def BooleanParameterType_template(item):
    # BooleanParameterType: representation of a boolean valued ScalarParameterType with two permissible values
    # "true" and "false"
    graql_insert_query = 'insert $booleanparametertype isa BooleanParameterType, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'BooleanParameterType',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'BooleanParameterType',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'BooleanParameterType',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'BooleanParameterType',
                               item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def UnitPrefix_template(item):
    # UnitPrefix: representation of a multiple or submultiple prefix for MeasurementUnits as defined in ISO/IEC 80000
    graql_insert_query = 'insert $unitprefix isa UnitPrefix, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has conversionFactor "' + item["conversionFactor"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'UnitPrefix',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'UnitPrefix',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'UnitPrefix',
                               item["iid"], 'isContained', 'HyperLink', i)

    return graql_insert_query

def LinearConversionUnit_template(item):
    # LinearConversionUnit: specialization of ConversionBasedUnit that represents a measurement unit that is defined
    # with respect to another reference measurement unit through a linear conversion relation with a conversion factor
    graql_insert_query = 'insert $linearconversionunit isa LinearConversionUnit, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has conversionFactor "' + item["conversionFactor"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'LinearConversionUnit',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'LinearConversionUnit',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'LinearConversionUnit',
                               item["iid"], 'isContained', 'HyperLink', i)

    write_relationship('Reference_referenceUnit', 'refersTo', 'LinearConversionUnit',
                       item["iid"], 'isReferredBy', 'MeasurementUnit', item["referenceUnit"])

    return graql_insert_query

def TimeOfDayParameterType_template(item):
    # TimeOfDayParameterType: representation of a time of day valued ScalarParameterType
    graql_insert_query = 'insert $timeofdayparametertype isa TimeOfDayParameterType, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'TimeOfDayParameterType',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'TimeOfDayParameterType',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'TimeOfDayParameterType',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'TimeOfDayParameterType',
                               item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def DateTimeParameterType_template(item):
    # DateTimeParameterType: representation of a calendar date and time valued ScalarParameterType
    graql_insert_query = 'insert $datetimeparametertype isa DateTimeParameterType, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"


    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'DateTimeParameterType',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'DateTimeParameterType',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'DateTimeParameterType',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'DateTimeParameterType',
                               item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def ArrayParameterType_template(item):
    # ArrayParameterType: specialization of CompoundParameterType that specifies a one-dimensional or multi-dimensional
    # array parameter type with elements (components) that are typed by other ScalarParameterTypes
    graql_insert_query = 'insert $arrayparametertype isa ArrayParameterType, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has isTensor "' + str(item["isTensor"]) + '"'
    graql_insert_query += ', has isFinalized "' + str(item["isFinalized"]) + '"'

    combinedDimension = ''
    for i in item["dimension"]:
        combinedDimension += str(i["v"]) + ' ,'
    graql_insert_query += ', has dimension "' + combinedDimension + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ArrayParameterType',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ArrayParameterType',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ArrayParameterType',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'ArrayParameterType',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["component"]:
        for i in item["component"]:
            write_relationship('Containment_component', 'contains', 'ArrayParameterType',
                               item["iid"], 'isContained', 'ParameterTypeComponent', i['v'])

    return graql_insert_query

def DerivedUnit_template(item):
    # DerivedUnit: specialization of MeasurementUnit that is defined as a product of powers of one or more other
    # measurement units
    graql_insert_query = 'insert $derivedunit isa DerivedUnit, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'DerivedUnit',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'DerivedUnit',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'DerivedUnit',
                               item["iid"], 'isContained', 'HyperLink', i)

    for i in item["unitFactor"]:
        write_relationship('Containment_unitFactor', 'contains', 'DerivedUnit',
                           item["iid"], 'isContained', 'UnitFactor', i['v'])

    return graql_insert_query

def ScaleValueDefinition_template(item):
    # ScaleValueDefinition: representation of a particular definitional scale value of a MeasurementScale
    graql_insert_query = 'insert $scalevaluedefinition isa ScaleValueDefinition, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has value "' + item["value"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ScaleValueDefinition',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ScaleValueDefinition',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ScaleValueDefinition',
                               item["iid"], 'isContained', 'HyperLink', i)

    return graql_insert_query

def DateParameterType_template(item):
    # DateParameterType: representation of a calendar date valued ScalarParameterType
    graql_insert_query = 'insert $dateparametertype isa DateParameterType, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'DateParameterType',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'DateParameterType',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'DateParameterType',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'DateParameterType',
                               item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def ParameterizedCategoryRule_template(item):
    # ParameterizedCategoryRule: Rule that asserts that one or more parameters of a given ParameterType should be
    # defined for CategorizableThings that are a member of the associated Category
    graql_insert_query = 'insert $parameterizedcategoryrule isa ParameterizedCategoryRule, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ParameterizedCategoryRule',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ParameterizedCategoryRule',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ParameterizedCategoryRule',
                               item["iid"], 'isContained', 'HyperLink', i)

    write_relationship('Reference_category', 'refersTo', 'ParameterizedCategoryRule', item["iid"],
                       'isReferredBy', 'Category', item["category"])

    for i in item["parameterType"]:
        write_relationship('Reference_parameterType', 'refersTo', 'ParameterizedCategoryRule', item["iid"],
                       'isReferredBy', 'ParameterType', i)

    return graql_insert_query

def SimpleUnit_template(item):
    # SimpleUnit: specialization of MeasurementUnit that represents a measurement unit that does not depend
    # on any other MeasurementUnit
    graql_insert_query = 'insert $simpleunit isa SimpleUnit, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'SimpleUnit',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'SimpleUnit',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'SimpleUnit',
                               item["iid"], 'isContained', 'HyperLink', i)

    return graql_insert_query

def CompoundParameterType_template(item):
    # CompoundParameterType: representation of a non-scalar compound parameter type that is composed of
    # one or more other (component) ParameterTypes
    graql_insert_query = 'insert $compoundparametertype isa CompoundParameterType, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has isFinalized "' + str(item["isFinalized"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'CompoundParameterType',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'CompoundParameterType',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'CompoundParameterType',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'CompoundParameterType',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["component"]:
        for i in item["component"]:
            write_relationship('Containment_component', 'contains', 'CompoundParameterType',
                               item["iid"], 'isContained', 'ParameterTypeComponent', i['v'])

    return graql_insert_query

def EnumerationParameterType_template(item):
    # EnumerationParameterType: representation of an enumeration valued ScalarParameterType with a user-defined list
    # of text values (enumeration literals) to select from
    graql_insert_query = 'insert $enumerationparametertype isa EnumerationParameterType, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has allowMultiSelect "' + str(item["allowMultiSelect"]) + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'EnumerationParameterType',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'EnumerationParameterType',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'EnumerationParameterType',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'EnumerationParameterType',
                               item["iid"], 'isReferredBy', 'Category', i)

    for i in item["valueDefinition"]:
        write_relationship('Containment_valueDefinition', 'contains', 'EnumerationParameterType',
                               item["iid"], 'isContained', 'ScaleValueDefinition', i["v"])

    return graql_insert_query

def OrdinalScale_template(item):
    # OrdinalScale: kind of MeasurementScale in which the possible valid values are ordered but
    # where the intervals between the values do not have particular significance
    graql_insert_query = 'insert $ordinalscale isa OrdinalScale, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has useShortNameValues "' + str(item["useShortNameValues"]) + '"'
    graql_insert_query += ', has numberSet "' + item["numberSet"] + '"'
    graql_insert_query += ', has isMinimumInclusive "' + str(item["isMinimumInclusive"]) + '"'
    graql_insert_query += ', has isMaximumInclusive "' + str(item["isMaximumInclusive"]) + '"'
    if item["minimumPermissibleValue"]:
        graql_insert_query += ', has minimumPermissibleValue "' + item["minimumPermissibleValue"] + '"'
    if item["maximumPermissibleValue"]:
        graql_insert_query += ', has maximumPermissibleValue "' + item["maximumPermissibleValue"] + '"'
    if item["positiveValueConnotation"]:
        graql_insert_query += ', has positiveValueConnotation "' + item["positiveValueConnotation"] + '"'
    if item["negativeValueConnotation"]:
        graql_insert_query += ', has negativeValueConnotation "' + item["negativeValueConnotation"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'OrdinalScale',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'OrdinalScale',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'OrdinalScale',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["valueDefinition"]:
        for i in item["valueDefinition"]:
            write_relationship('Containment_valueDefinition', 'contains', 'OrdinalScale',
                               item["iid"], 'isContained', 'ScaleValueDefinition', i)

    if item["mappingToReferenceScale"]:
        for i in item["mappingToReferenceScale"]:
            write_relationship('Containment_mappingToReferenceScale', 'contains',
                               'OrdinalScale',
                               item["iid"], 'isContained', 'MappingToReferenceScale', i)

    write_relationship('Reference_unit', 'refersTo', 'OrdinalScale',
                       item["iid"], 'isReferredBy', 'MeasurementUnit', item["unit"])

    return graql_insert_query

def Glossary_template(item):
    # Glossary: representation of a glossary of terms
    graql_insert_query = 'insert $glossary isa Glossary, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'Glossary',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'Glossary',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'Glossary',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'Glossary',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["term"]:
        for i in item["term"]:
            write_relationship('Containment_term', 'contains', 'Glossary',
                               item["iid"], 'isContained', 'Term', i)

    return graql_insert_query

def SpecializedQuantityKind_template(item):
    # SpecializedQuantityKind: specialization of QuantityKind that represents a kind of quantity that is
    # a specialization of another kind of quantity
    graql_insert_query = 'insert $specializedquantitykind isa SpecializedQuantityKind, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    if item["quantityDimensionSymbol"]:
        graql_insert_query += ', has quantityDimensionSymbol "' + item["quantityDimensionSymbol"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'SpecializedQuantityKind',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'SpecializedQuantityKind',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'SpecializedQuantityKind',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'SpecializedQuantityKind',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["possibleScale"]:
        for i in item["possibleScale"]:
            write_relationship('Reference_possibleScale', 'refersTo', 'SpecializedQuantityKind',
                               item["iid"], 'isReferredBy', 'MeasurementScale', i)

    write_relationship('Reference_defaultScale', 'refersTo', 'SpecializedQuantityKind',
                       item["iid"], 'isReferredBy', 'MeasurementScale', item["defaultScale"])

    write_relationship('Reference_general', 'refersTo', 'SpecializedQuantityKind',
                       item["iid"], 'isReferredBy', 'QuantityKind', item["general"])
    #ToDo
    '''
    has quantityDimensionExpression,  
    has quantityDimensionExponent, 
    has numberOfValues,        
    plays refers_allPossibleScale    
    '''

    return graql_insert_query

# -------------------------------------------------------------
# 9 Templates for Classes found in SiteDirectory json file
# -------------------------------------------------------------

'''
SiteDirectory
SiteReferenceDataLibrary
Person
ModelReferenceDataLibrary
EmailAddress
DomainOfExpertise
EngineeringModelSetup
IterationSetup
Participant
'''

def SiteDirectory_template(item):
    # SiteDirectory: resource directory that contains (references to) the data that is used across all models,
    # templates, catalogues and reference data for a specific concurrent design centre
    graql_insert_query = 'insert $sitedirectory isa SiteDirectory, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '", has lastModifiedOn "' + item["modifiedOn"] +'"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ";"

    if item["organization"]:
        for i in item["organization"]:
            write_relationship('Containment_organization', 'contains', 'SiteDirectory',
                               item["iid"], 'isContained', 'Organization', i)

    if item["person"]:
        for i in item["person"]:
            write_relationship('Containment_person', 'contains', 'SiteDirectory',
                               item["iid"], 'isContained', 'Person', i)

    if item["participantRole"]:
        for i in item["participantRole"]:
            write_relationship('Containment_participantRole', 'contains', 'SiteDirectory',
                               item["iid"], 'isContained', 'ParticipantRole', i)

    if item["model"]:
        for i in item["model"]:
            write_relationship('Containment_model', 'contains', 'SiteDirectory',
                               item["iid"], 'isContained', 'EngineeringModelSetup', i)

    if item["personRole"]:
        for i in item["personRole"]:
            write_relationship('Containment_personRole', 'contains', 'SiteDirectory',
                               item["iid"], 'isContained', 'PersonRole', i)

    if item["logEntry"]:
        for i in item["logEntry"]:
            write_relationship('Containment_logEntry', 'contains', 'SiteDirectory',
                               item["iid"], 'isContained', 'SiteLogEntry', i)

    if item["domainGroup"]:
        for i in item["domainGroup"]:
            write_relationship('Containment_domainGroup', 'contains', 'SiteDirectory',
                               item["iid"], 'isContained', 'DomainOfExpertiseGroup', i)

    if item["domain"]:
        for i in item["domain"]:
            write_relationship('Containment_domain', 'contains', 'SiteDirectory',
                               item["iid"], 'isContained', 'DomainOfExpertise', i)

    if item["naturalLanguage"]:
        for i in item["naturalLanguage"]:
            write_relationship('Containment_naturalLanguage', 'contains', 'SiteDirectory',
                               item["iid"], 'isContained', 'NaturalLanguage', i)

    if item["siteReferenceDataLibrary"]:
        for i in item["siteReferenceDataLibrary"]:
            write_relationship('Containment_siteReferenceDataLibrary', 'contains', 'SiteDirectory',
                               item["iid"], 'isContained', 'SiteReferenceDataLibrary', i)

    if item["defaultParticipantRole"]:
        write_relationship('Reference_defaultParticipantRole', 'refersTo',
                           'SiteDirectory', item["iid"], 'isReferredBy', 'ParticipantRole',
                           item["defaultParticipantRole"])

    if item["defaultPersonRole"]:
        write_relationship('Reference_defaultPersonRole', 'refersTo',
                           'SiteDirectory', item["iid"], 'isReferredBy', 'PersonRole', item["defaultPersonRole"])

    return graql_insert_query

def SiteReferenceDataLibrary_template(item):
    # SiteReferenceDataLibrary: ReferenceDataLibrary that can be (re-)used by multiple EngineeringModels /
    # EngineeringModelSetups
    graql_insert_query = 'insert $sitereferencedatalibrary isa SiteReferenceDataLibrary, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["definedCategory"]:
        for i in item["definedCategory"]:
            write_relationship('Containment_definedCategory', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'Category', i)
    if item["parameterType"]:
        for i in item["parameterType"]:
            write_relationship('Containment_parameterType', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'ParameterType', i)
    if item["parameterType"]:
        for i in item["parameterType"]:
            write_relationship('Containment_parameterType', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'ParameterType', i)

    if item["scale"]:
        for i in item["scale"]:
            write_relationship('Containment_scale', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'MeasurementScale', i)

    if item["unitPrefix"]:
        for i in item["unitPrefix"]:
            write_relationship('Containment_unitPrefix', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'UnitPrefix', i)

    if item["unit"]:
        for i in item["unit"]:
            write_relationship('Containment_unit', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'MeasurementUnit', i)

    if item["fileType"]:
        for i in item["fileType"]:
            write_relationship('Containment_fileType', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'FileType', i)

    if item["glossary"]:
        for i in item["glossary"]:
            write_relationship('Containment_glossary', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'Glossary', i)

    if item["referenceSource"]:
        for i in item["referenceSource"]:
            write_relationship('Containment_referenceSource', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'ReferenceSource', i)

    if item["rule"]:
        for i in item["rule"]:
            write_relationship('Containment_rule', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'Rule', i)

    if item["constant"]:
        for i in item["constant"]:
            write_relationship('Containment_constant', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'Constant', i)

    if item["baseQuantityKind"]:
        for i in item["baseQuantityKind"]:
            write_relationship('Reference_baseQuantityKind', 'refersTo', 'SiteReferenceDataLibrary',
                               item["iid"], 'isReferredBy', 'QuantityKind', i["v"])

    if item["baseUnit"]:
        for i in item["baseUnit"]:
            write_relationship('Reference_baseUnit', 'refersTo', 'SiteReferenceDataLibrary',
                               item["iid"], 'isReferredBy', 'MeasurementUnit', i)

    if item["requiredRdl"]:
        write_relationship('Reference_requiredRdl', 'refersTo', 'SiteReferenceDataLibrary',
                           item["iid"], 'isReferredBy', 'SiteReferenceDataLibrary', item["requiredRdl"])


    return graql_insert_query

def Person_template(item):
    # Person: representation of a physical person that is a potential Participant in a concurrent engineering activity
    graql_insert_query = 'insert $person isa Person, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has isActive "' + str(item["isActive"]) + '"'
    graql_insert_query += ', has givenName "' + item["givenName"] + '"'
    graql_insert_query += ', has surname "' + item["surname"] + '"'
    if item["organizationalUnit"]:
        graql_insert_query += ', has organizationalUnit "' + item["organizationalUnit"] + '"'
    if item["password"]:
        graql_insert_query += ', has password "' + item["password"] + '"'
    graql_insert_query += ";"

    if item["emailAddress"]:
        for i in item["emailAddress"]:
            write_relationship('Containment_emailAddress', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'EmailAddress', i)

    if item["telephoneNumber"]:
        for i in item["telephoneNumber"]:
            write_relationship('Containment_telephoneNumber', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'TelephoneNumber', i)

    if item["userPreference"]:
        for i in item["userPreference"]:
            write_relationship('Containment_userPreference', 'contains', 'SiteReferenceDataLibrary',
                               item["iid"], 'isContained', 'UserPreference', i)

    if item["organization"]:
        write_relationship('Reference_organization', 'refersTo', 'SiteReferenceDataLibrary',
                           item["iid"], 'isReferredBy', 'Organization', item["organization"])

    if item["defaultDomain"]:
        write_relationship('Reference_defaultDomain', 'refersTo', 'SiteReferenceDataLibrary',
                           item["iid"], 'isReferredBy', 'DomainOfExpertise', item["defaultDomain"])

    if item["role"]:
        write_relationship('Reference_role', 'refersTo', 'SiteReferenceDataLibrary',
                           item["iid"], 'isReferredBy', 'PersonRole', item["role"])

    if item["defaultEmailAddress"]:
        write_relationship('Reference_defaultEmailAddress', 'refersTo', 'SiteReferenceDataLibrary',
                           item["iid"], 'isReferredBy', 'EmailAddress', item["defaultEmailAddress"])

    if item["defaultTelephoneNumber"]:
        write_relationship('Reference_defaultTelephoneNumber', 'refersTo', 'SiteReferenceDataLibrary',
                           item["iid"], 'isReferredBy', 'TelephoneNumber', item["defaultTelephoneNumber"])

    return graql_insert_query

def ModelReferenceDataLibrary_template(item):
    # ModelReferenceDataLibrary: ReferenceDataLibrary that is particular to a given EngineeringModel
    # / EngineeringModelSetup
    graql_insert_query = 'insert $modelreferencedatalibrary isa ModelReferenceDataLibrary, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ModelReferenceDataLibrary',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ModelReferenceDataLibrary',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ModelReferenceDataLibrary',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["definedCategory"]:
        for i in item["definedCategory"]:
            write_relationship('Containment_definedCategory', 'contains', 'ModelReferenceDataLibrary',
                               item["iid"], 'isContained', 'Category', i)

    if item["parameterType"]:
        for i in item["parameterType"]:
            write_relationship('Containment_parameterType', 'contains', 'ModelReferenceDataLibrary',
                               item["iid"], 'isContained', 'ParameterType', i)

    if item["scale"]:
        for i in item["scale"]:
            write_relationship('Containment_scale', 'contains', 'ModelReferenceDataLibrary',
                               item["iid"], 'isContained', 'MeasurementScale', i)

    if item["unitPrefix"]:
        for i in item["unitPrefix"]:
            write_relationship('Containment_unitPrefix', 'contains', 'ModelReferenceDataLibrary',
                               item["iid"], 'isContained', 'UnitPrefix', i)

    if item["unit"]:
        for i in item["unit"]:
            write_relationship('Containment_unit', 'contains', 'ModelReferenceDataLibrary',
                               item["iid"], 'isContained', 'MeasurementUnit', i)

    if item["fileType"]:
        for i in item["fileType"]:
            write_relationship('Containment_fileType', 'contains', 'ModelReferenceDataLibrary',
                               item["iid"], 'isContained', 'FileType', i)

    if item["glossary"]:
        for i in item["glossary"]:
            write_relationship('Containment_glossary', 'contains', 'ModelReferenceDataLibrary',
                               item["iid"], 'isContained', 'Glossary', i)

    if item["referenceSource"]:
        for i in item["referenceSource"]:
            write_relationship('Containment_referenceSource', 'contains', 'ModelReferenceDataLibrary',
                               item["iid"], 'isContained', 'ReferenceSource', i)

    if item["rule"]:
        for i in item["rule"]:
            write_relationship('Containment_rule', 'contains', 'ModelReferenceDataLibrary',
                               item["iid"], 'isContained', 'Rule', i)

    if item["constant"]:
        for i in item["constant"]:
            write_relationship('Containment_constant', 'contains', 'ModelReferenceDataLibrary',
                               item["iid"], 'isContained', 'Constant', i)

    if item["baseQuantityKind"]:
        for i in item["baseQuantityKind"]:
            write_relationship('Reference_baseQuantityKind', 'refersTo', 'ModelReferenceDataLibrary',
                               item["iid"], 'isReferredBy', 'QuantityKind', i["v"])

    if item["baseUnit"]:
        for i in item["baseUnit"]:
            write_relationship('Reference_baseUnit', 'refersTo', 'ModelReferenceDataLibrary',
                               item["iid"], 'isReferredBy', 'MeasurementUnit', i)

    if item["requiredRdl"]:
        write_relationship('Reference_requiredRdl', 'refersTo', 'ModelReferenceDataLibrary',
                           item["iid"], 'isReferredBy', 'SiteReferenceDataLibrary', item["requiredRdl"])

    return graql_insert_query

def EmailAddress_template(item):
    # EmailAddress: representation of an e-mail address
    graql_insert_query = 'insert $emailaddress isa EmailAddress, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has vcardType "' + item["vcardType"] + '"'
    graql_insert_query += ', has value "' + item["value"] + '"'
    graql_insert_query += ";"
    return graql_insert_query

def DomainOfExpertise_template(item):
    # DomainOfExpertise: representation of a coherent set of experience, skills, methods, standards and tools in
    # a specific field of knowledge relevant to an engineering process
    graql_insert_query = 'insert $domainofexpertise isa DomainOfExpertise, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'DomainOfExpertise',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'DomainOfExpertise',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'DomainOfExpertise',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'DomainOfExpertise',
                               item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def EngineeringModelSetup_template(item):
    # EngineeringModelSetup: representation of the set-up information of a concurrent engineering model
    graql_insert_query = 'insert $engineeringmodelsetup isa EngineeringModelSetup, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has kind "' + item["kind"] + '"'
    graql_insert_query += ', has studyPhase "' + item["studyPhase"] + '"'
    graql_insert_query += ', has engineeringModelIid "' + item["engineeringModelIid"] + '"'
    if item["sourceEngineeringModelSetupIid"]:
        graql_insert_query += ', has sourceEngineeringModelSetupIid "' + item["sourceEngineeringModelSetupIid"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'EngineeringModelSetup',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'EngineeringModelSetup',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'EngineeringModelSetup',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["participant"]:
        for i in item["participant"]:
            write_relationship('Containment_participant', 'contains', 'EngineeringModelSetup',
                               item["iid"], 'isContained', 'Participant', i)

    write_relationship('Containment_requiredRdl', 'contains', 'EngineeringModelSetup',
                       item["iid"], 'isContained', 'ModelReferenceDataLibrary', i)

    for i in item["iterationSetup"]:
        write_relationship('Containment_iterationSetup', 'contains', 'EngineeringModelSetup',
                           item["iid"], 'isContained', 'IterationSetup', i)

    for i in item["activeDomain"]:
        write_relationship('Reference_activeDomain', 'refersTo', 'EngineeringModelSetup',
                           item["iid"], 'isReferredBy', 'DomainOfExpertise', i)

    return graql_insert_query

def IterationSetup_template(item):
    # IterationSetup: representation of the set-up information of an Iteration in the EngineeringModel associated
    # with the EngineeringModelSetup that contains this IterationInfo
    graql_insert_query = 'insert $iterationsetup isa IterationSetup, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has iterationIid "' + item["iterationIid"] + '"'
    graql_insert_query += ', has iterationNumber "' + str(item["iterationNumber"]) +'"'
    graql_insert_query += ', has description "' + item["description"] + '"'
    graql_insert_query += ', has isDeleted "' + str(item["isDeleted"]) + '"'
    if item["frozenOn"]:
        graql_insert_query += ', has frozenOn "' + item["frozenOn"] + '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ";"

    if item["sourceIterationSetup"]:
        write_relationship('Reference_sourceIterationSetup', 'refersTo', 'IterationSetup',
                           item["iid"], 'isReferredBy', 'IterationSetup', item["sourceIterationSetup"])

    return graql_insert_query

def Participant_template(item):
    # Participant: representation of a participant in the team working in a concurrent engineering activity on
    # an EngineeringModel
    graql_insert_query = 'insert $participant isa Participant, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has isActive "' + str(item["isActive"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_role', 'refersTo', 'Participant',
                           item["iid"], 'isReferredBy', 'PersonRole', item["role"])

    write_relationship('Reference_person', 'refersTo', 'Participant',
                       item["iid"], 'isReferredBy', 'Person', item["person"])

    write_relationship('Reference_selectedDomain', 'refersTo', 'Participant',
                       item["iid"], 'isReferredBy', 'DomainOfExpertise', item["selectedDomain"])

    for i in item["domain"]:
        write_relationship('Reference_domain', 'refersTo', 'Participant',
                               item["iid"], 'isReferredBy', 'DomainOfExpertise', i)


    return graql_insert_query

# -------------------------------------------------------------
# 1 Template for Class found in Engineering Model Header json file
# -------------------------------------------------------------
def EngineeringModel_template(item):
    # EngineeringModel: representation of a parametric concurrent engineering model that specifies the problem to be
    # solved and defines one or more (possible) design solutions
    graql_insert_query = 'insert $engineeringmodel isa EngineeringModel, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '", has lastModifiedOn "' + item["modifiedOn"] +'"'
    graql_insert_query += ";"

    if item["logEntry"]:
        for i in item["logEntry"]:
            write_relationship('Containment_logEntry', 'contains', 'EngineeringModel',
                               item["iid"], 'isContained', 'ModelLogEntry', i)

    write_relationship('Reference_engineeringModelSetup', 'refersTo', 'EngineeringModel',
                       item["iid"], 'isReferredBy', 'EngineeringModelSetup',
                       item["engineeringModelSetup"])

    if item["commonFileStore"]:
        write_relationship('Containment_commonFileStore', 'contains', 'EngineeringModel',
                           item["iid"], 'isContained', 'CommonFileStore',
                           item["commonFileStore"])

    for i in item["iteration"]:
        write_relationship('Containment_iteration', 'contains', 'EngineeringModel',
                           item["iid"], 'isContained', 'Iteration', i)

    return graql_insert_query


# -------------------------------------------------------------
# 64 Template for remaining classes
# -------------------------------------------------------------

'''
ActualFiniteState
ActualFiniteStateList
AndExpression
BinaryRelationship
BooleanExpression
BuiltInRuleVerification
CommonFileStore
CompoundParameterType
ConversionBasedUnit
DefinedThing
DomainOfExpertiseGroup

ElementBase
ExclusiveOrExpression
ExternalIdentifierMap
File
FileRevision
FileStore
Folder
IdCorrespondence
MeasurementScale
MeasurementUnit
ModelLogEntry

MultiRelationship
MultiRelationshipRule
NaturalLanguage
NestedElement
NestedParameter
NotExpression
OrExpression
Organization
ParameterBase
ParameterOrOverrideBase
ParameterOverride

ParameterOverrideValueSet
ParameterType
ParameterValueSetBase
ParametricConstraint
ParticipantPermission
ParticipantRole
PersonPermission
PersonRole
PossibleFiniteState
PossibleFiniteStateList
QuantityKind
ReferenceDataLibrary
ReferencerRule
RelationalExpression
Relationship
Requirement
RequirementsContainer
RequirementsGroup
Rule
RuleVerification
RuleVerificationList

RuleViolation
ScalarParameterType
SimpleParameterValue
SimpleParameterizableThing
SiteLogEntry
TelephoneNumber
TopContainer
UserPreference
UserRuleVerification
Thing
'''

def ActualFiniteState_template(item):
    # ActualFiniteState: representation of an actual finite state in an ActualFiniteStateList
    graql_insert_query = 'insert $actualfinitestate isa ActualFiniteState, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    #graql_insert_query += ', has name "' + item["name"] + '"'
    #graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has kind "' + item["kind"] + '"'
    graql_insert_query += ";"
    # ToDo
    # write_relationship('Reference_owner', 'refersTo', 'ActualFiniteState', item["iid"],
    #                        'isReferredBy', 'DomainOfExpertise', item["owner"])

    for i in item['possibleState']:
        write_relationship('Reference_possibleState', 'refersTo', 'ActualFiniteState', item["iid"],
                           'isReferredBy', 'PossibleFiniteState', i)

    return graql_insert_query

def ActualFiniteStateList_template(item):
    # ActualFiniteStateList: representation of a set of actual finite states that can be used to define a finite
    # state dependence for a Parameter
    graql_insert_query = 'insert $actualfinitestatelist isa ActualFiniteStateList, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    #graql_insert_query += ', has name "' + item["name"] + '"'
    #graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refersTo', 'ActualFiniteStateList', item["iid"],
                           'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["excludeOption"]:
        for i in item["excludeOption"]:
            write_relationship('Reference_excludeOption', 'refersTo', 'ActualFiniteStateList', item["iid"],
                               'isReferredBy', 'Option', i)

    for i in item["possibleFiniteStateList"]:
        write_relationship('Reference_possibleFiniteStateList', 'refersTo', 'ActualFiniteStateList',
                           item["iid"], 'isReferredBy', 'PossibleFiniteStateList', i['v'])

    if item["actualState"]:
        for i in item["actualState"]:
            write_relationship('Containment_actualState', 'contains', 'ActualFiniteStateList', item["iid"],
                               'isContained', 'ActualFiniteState', i)
    return graql_insert_query

def AndExpression_template(item):
    # AndExpression: representation of a boolean and (conjunction) expression
    graql_insert_query = 'insert $andexpression isa AndExpression, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ";"

    for i in item["term"]:
        write_relationship('Reference_term', 'refersTo', 'AndExpression',
                           item["iid"], 'isReferredBy', 'BooleanExpression', i)
    return graql_insert_query

def BinaryRelationship_template(item):
    # BinaryRelationship: representation of a relationship between exactly two Things
    graql_insert_query = 'insert $binaryrelationship isa BinaryRelationship, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ";"

    write_relationship('Reference_source', 'refersTo', 'BinaryRelationship',
                       item["iid"], 'isReferredBy', 'Thing', item["source"])

    write_relationship('Reference_target', 'refersTo', 'BinaryRelationship',
                       item["iid"], 'isReferredBy', 'Thing', item["target"])

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'BinaryRelationship',
                               item["iid"], 'isReferredBy', 'Category', i)

    write_relationship('Reference_owner', 'refersTo', 'BinaryRelationship', item["iid"],
                   'isReferredBy', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def BooleanExpression_template(item):
    # BooleanExpression: abstract supertype to provide a common base for all kinds of boolean expression
    graql_insert_query = 'insert $booleanexpression isa BooleanExpression, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ";"

    return graql_insert_query

def BuiltInRuleVerification_template(item):
    # BuiltInRuleVerification: representation of the verification of a built-in data model rule
    graql_insert_query = 'insert $builtinruleverification isa BuiltInRuleVerification, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has isActive "' + str(item["isActive"]) + '"'
    if item["executedOn"]:
        graql_insert_query += ', has executedOn "' + item["executedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has status "' + item["status"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refersTo', 'BuiltInRuleVerification', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["violation"]:
        for i in item["violation"]:
            write_relationship('Containment_violation', 'contains', 'BuiltInRuleVerification',
                               item["iid"], 'isContained', 'RuleViolation', i)

    return graql_insert_query

def CommonFileStore_template(item):
    # CommonFileStore: representation of a common FileStore for use by all Participants
    graql_insert_query = 'insert $commonfilestore isa CommonFileStore, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ";"

    if item["folder"]:
        for i in item["folder"]:
            write_relationship('Containment_folder', 'contains', 'CommonFileStore', item["iid"],
                               'isContained', 'Folder', i)
    if item["file"]:
        for i in item["file"]:
            write_relationship('Containment_file', 'contains', 'CommonFileStore', item["iid"],
                               'isContained', 'File', i)

    write_relationship('Reference_owner', 'refersTo', 'CommonFileStore', item["iid"],
                   'isReferredBy', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def ConversionBasedUnit_template(item):
    # ConversionBasedUnit: abstract specialization of MeasurementUnit that represents a measurement unit that is
    # defined with respect to another reference unit through an explicit conversion relation
    graql_insert_query = 'insert $conversionbasedunit isa ConversionBasedUnit, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has conversionFactor "' + item["conversionFactor"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_referenceUnit', 'refersTo', 'ConversionBasedUnit',
                       item["iid"], 'isReferredBy', 'MeasurementUnit', item["referenceUnit"])


    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ConversionBasedUnit',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ConversionBasedUnit',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ConversionBasedUnit',
                               item["iid"], 'isContained', 'HyperLink', i)

    return graql_insert_query

def DefinedThing_template(item):
    # DefinedThing: abstract specialization of Thing for all classes that need a human readable definition, i.e. a name
    # and a short name, and optionally explicit textual definitions, aliases and hyperlinks
    graql_insert_query = 'insert $definedthing isa DefinedThing, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'DefinedThing',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'DefinedThing',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'DefinedThing',
                               item["iid"], 'isContained', 'HyperLink', i)


    return graql_insert_query

def DomainOfExpertiseGroup_template(item):
    # DomainOfExpertiseGroup: representation of a group of domains of expertise (DomainOfExpertise) defined for
    # this SiteDirectory
    graql_insert_query = 'insert $domainofexpertisegroup isa DomainOfExpertiseGroup, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'DomainOfExpertiseGroup',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'DomainOfExpertiseGroup',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'DomainOfExpertiseGroup',
                               item["iid"], 'isContained', 'HyperLink', i)

    for i in item["domain"]:
        write_relationship('Reference_domain', 'refersTo', 'DomainOfExpertiseGroup',
                               item["iid"], 'isReferredBy', 'DomainOfExpertise', i)

    return graql_insert_query

def ElementBase_template(item):
    # ElementBase: abstract superclass of ElementDefinition, ElementUsage and NestedElement that captures
    # their common properties and allows to refer to either of them
    graql_insert_query = 'insert $elementbase isa ElementBase, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ElementBase',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ElementBase',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ElementBase',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'ElementBase',
                                   item["iid"], 'isReferredBy', 'Category', i)

    write_relationship('Reference_owner', 'refersTo', 'ElementBase', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def ExclusiveOrExpression_template(item):
    # ExclusiveOrExpression: representation of a boolean exclusive or expression
    graql_insert_query = 'insert $exclusiveorexpression isa ExclusiveOrExpression, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ";"

    for i in item["term"]:
        write_relationship('Reference_term', 'refersTo', 'ExclusiveOrExpression',
                           item["iid"], 'isReferredBy', 'BooleanExpression', i)

    return graql_insert_query

def ExternalIdentifierMap_template(item):
    # ExternalIdentifierMap: representation of a mapping that relates E-TM-10-25 instance UUIDs to identifiers of
    # corresponding items in an external tool / model
    graql_insert_query = 'insert $externalidentifiermap isa ExternalIdentifierMap, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has externalModelName "' + item["externalModelName"] + '"'
    graql_insert_query += ', has externalToolName "' + item["externalToolName"] + '"'
    if item["externalToolVersion"]:
        graql_insert_query += ', has externalToolVersion "' + item["externalToolVersion"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refersTo', 'ExternalIdentifierMap', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["correspondence"]:
        for i in item["correspondence"]:
            write_relationship('Containment_correspondence', 'contains', 'ExternalIdentifierMap',
                               item["iid"], 'isContained', 'IdCorrespondence', i)

    if item["externalFormat"]:
        write_relationship('Reference_externalFormat', 'refersTo', 'ExternalIdentifierMap', item["iid"],
                           'isReferredBy', 'ReferenceSource', item["externalFormat"])

    return graql_insert_query

def File_template(item):
    # File: representation of a computer file
    graql_insert_query = 'insert $file isa File, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ";"

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'File',
                               item["iid"], 'isReferredBy', 'Category', i)

    write_relationship('Reference_owner', 'refersTo', 'File', item["iid"],
                   'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["lockedBy"]:
        write_relationship('Reference_lockedBy', 'refersTo', 'File', item["iid"],
                           'isReferredBy', 'Person', item["lockedBy"])

    for i in item["fileRevision"]:
        write_relationship('Containment_fileRevision', 'contains', 'File',
                           item["iid"], 'isContained', 'FileRevision', i)

    return graql_insert_query

def FileRevision_template(item):
    # FileRevision: representation of a persisted revision of a File
    graql_insert_query = 'insert $filerevision isa FileRevision, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has contentHash "' + item["contentHash"] + '"'
    graql_insert_query += ', has path "' + item["path"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_creator', 'refersTo', 'FileRevision', item["iid"],
                       'isReferredBy', 'Participant', item["creator"])

    if item["containingFolder"]:
        write_relationship('Reference_containingFolder', 'refersTo', 'FileRevision', item["iid"],
                           'isReferredBy', 'Folder', item["containingFolder"])

    for i in item["fileType"]:
        write_relationship('Reference_fileType', 'refersTo', 'FileRevision', item["iid"],
                           'isReferredBy', 'FileType', i)

    return graql_insert_query

def FileStore_template(item):
    # FileStore: data container that may hold zero or more (possibly nested) Folders and Files
    graql_insert_query = 'insert $filestore isa FileStore, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ";"

    if item["folder"]:
        for i in item["folder"]:
            write_relationship('Containment_folder', 'contains', 'FileStore', item["iid"],
                               'isContained', 'Folder', i)
    if item["file"]:
        for i in item["file"]:
            write_relationship('Containment_file', 'contains', 'FileStore', item["iid"],
                               'isContained', 'File', i)

    write_relationship('Reference_owner', 'refersTo', 'FileStore', item["iid"],
                   'isReferredBy', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def Folder_template(item):
    # Folder: representation of a named folder in a FileStore that may contain files and other folders
    graql_insert_query = 'insert $folder isa Folder, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has path "' + item["path"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_creator', 'refersTo', 'Folder', item["iid"],
                       'isReferredBy', 'Participant', item["creator"])

    if item["containingFolder"]:
        write_relationship('Reference_containingFolder', 'refersTo', 'Folder', item["iid"],
                           'isReferredBy', 'Folder', item["containingFolder"])

    write_relationship('Reference_owner', 'refersTo', 'Folder', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def IdCorrespondence_template(item):
    # IdCorrespondence: representation of a correspondence mapping between a single Thing
    # (identified through its iid) and an external identifier

    graql_insert_query = 'insert $idcorrespondence isa IdCorrespondence, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has internalThing "' + item["internalThing"] + '"'
    graql_insert_query += ', has externalId "' + item["externalId"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refersTo', 'IdCorrespondence', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def MeasurementScale_template(item):
    # MeasurementScale: representation of a measurement scale to express quantity values for a numerical Parameter,
    # i.e. a Parameter that is typed by a QuantityKind
    graql_insert_query = 'insert $measurementscale isa MeasurementScale, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has numberSet "' + item["numberSet"] + '"'
    graql_insert_query += ', has isMinimumInclusive "' + str(item["isMinimumInclusive"]) + '"'
    graql_insert_query += ', has isMaximumInclusive "' + str(item["isMaximumInclusive"]) + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'

    if item["minimumPermissibleValue"]:
        graql_insert_query += ', has minimumPermissibleValue "' + item["minimumPermissibleValue"] + '"'
    if item["maximumPermissibleValue"]:
        graql_insert_query += ', has maximumPermissibleValue "' + item["maximumPermissibleValue"] + '"'
    if item["positiveValueConnotation"]:
        graql_insert_query += ', has positiveValueConnotation "' + item["positiveValueConnotation"] + '"'
    if item["negativeValueConnotation"]:
        graql_insert_query += ', has negativeValueConnotation "' + item["negativeValueConnotation"] + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'MeasurementScale',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'MeasurementScale',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'MeasurementScale',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["valueDefinition"]:
        for i in item["valueDefinition"]:
            write_relationship('Containment_valueDefinition', 'contains', 'MeasurementScale',
                               item["iid"], 'isContained', 'ScaleValueDefinition', i)

    if item["mappingToReferenceScale"]:
        for i in item["mappingToReferenceScale"]:
            write_relationship('Containment_mappingToReferenceScale', 'contains',
                               'MeasurementScale',
                               item["iid"], 'isContained', 'MappingToReferenceScale', i)

    write_relationship('Reference_unit', 'refersTo', 'MeasurementScale',
                       item["iid"], 'isReferredBy', 'MeasurementUnit', item["unit"])

    return graql_insert_query

def MeasurementUnit_template(item):
    # MeasurementUnit: abstract superclass that represents the [VIM] concept of "measurement unit" that is defined as
    # "real scalar quantity, defined and adopted by convention, with which any other quantity of the same kind can be
    # compared to express the ratio of the two quantities as a number"
    graql_insert_query = 'insert $measurementunit isa MeasurementUnit, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'MeasurementUnit',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'MeasurementUnit',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'MeasurementUnit',
                               item["iid"], 'isContained', 'HyperLink', i)

    return graql_insert_query

def ModelLogEntry_template(item):
    # ModelLogEntry: representation of a logbook entry for an EngineeringModel
    graql_insert_query = 'insert $modellogentry isa ModelLogEntry, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has languageCode "' + item["languageCode"] + '"'
    graql_insert_query += ', has content "' + item["content"] + '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ', has level "' + item["level"] + '"'

    if item["affectedItemIid"]:
        # Combine all notes into 1
        combined=''
        for i in item["affectedItemIid"]:
            combined += i + ' ,'
        graql_insert_query += ', has affectedItemIid "' + combined + '"'

    graql_insert_query += ";"

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'ModelLogEntry',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["author"]:
        write_relationship('Reference_author', 'refersTo', 'ModelLogEntry',
                           item["iid"], 'isReferredBy', 'Person', item["author"])

    return graql_insert_query

def MultiRelationship_template(item):
    # MultiRelationship: representation of a relationship between multiple Things
    graql_insert_query = 'insert $multirelationship isa MultiRelationship, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ";"

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'MultiRelationship',
                               item["iid"], 'isReferredBy', 'Category', i)

    write_relationship('Reference_owner', 'refersTo', 'MultiRelationship', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["relatedThing"]:
        for i in item["relatedThing"]:
            write_relationship('Reference_relatedThing', 'refersTo', 'MultiRelationship',
                               item["iid"], 'isReferredBy', 'Thing', i)

    return graql_insert_query

def MultiRelationshipRule_template(item):
    # MultiRelationshipRule: representation of a validation rule for MultiRelationships that relate (potentially)
    # more than two CategorizableThings
    graql_insert_query = 'insert $multirelationshiprule isa MultiRelationshipRule, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has minRelated ' + str(item["minRelated"])
    graql_insert_query += ', has maxRelated ' + str(item["maxRelated"])
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'MultiRelationshipRule',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'MultiRelationshipRule',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'MultiRelationshipRule',
                               item["iid"], 'isContained', 'HyperLink', i)

    write_relationship('Reference_relationCategory', 'refersTo', 'MultiRelationshipRule',
                       item["iid"], 'isReferredBy', 'Category', item["relationshipCategory"])

    for i in item["relatedCategory"]:
        write_relationship('Reference_relatedCategory', 'refersTo', 'MultiRelationshipRule',
                           item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def NaturalLanguage_template(item):
    # NaturalLanguage: representation of a known natural language
    graql_insert_query = 'insert $naturallanguage isa NaturalLanguage, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has languageCode "' + item["languageCode"] + '"'
    graql_insert_query += ', has nativeName "' + item["nativeName"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

def NestedElement_template(item):
    # NestedElement: representation of an explicit element of a system-of-interest in a fully expanded architectural
    # decomposition tree for one Option
    graql_insert_query = 'insert $nestedelement isa NestedElement, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isVolatile "' + str(item["isVolatile"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refersTo', 'NestedElement', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["nestedParameter"]:
        for i in item["nestedParameter"]:
            write_relationship('Containment_nestedParameter', 'contains', 'NestedElement',
                               item["iid"], 'isContained', 'NestedParameter', i)

    write_relationship('Reference_rootElement', 'refersTo', 'NestedElement', item["iid"],
                       'isReferredBy', 'ElementDefinition', item["rootElement"])

    for i in item["elementUsage"]:
        write_relationship('Reference_elementUsage', 'refersTo', 'NestedElement',
                           item["iid"], 'isReferredBy', 'ElementUsage', i)

    return graql_insert_query

def NestedParameter_template(item):
    # NestedParameter: representation of a parameter with a value of a NestedElement
    graql_insert_query = 'insert $nestedparameter isa NestedParameter, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has path "' + item["path"] + '"'
    graql_insert_query += ', has formula "' + clean(item["formula"]) + '"'
    graql_insert_query += ', has isVolatile "' + str(item["isVolatile"]) + '"'
    graql_insert_query += ', has actualValue "' + str(item["actualValue"]) + '"'
    graql_insert_query += ";"

    if item["actualState"]:
        write_relationship('Reference_actualState', 'refersTo', 'NestedParameter', item["iid"],
                           'isReferredBy', 'ActualFiniteState', item["actualState"])

    write_relationship('Reference_owner', 'refersTo', 'NestedParameter', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    write_relationship('Reference_associatedParameter', 'refersTo', 'NestedParameter', item["iid"],
                       'isReferredBy', 'ParameterBase', item["associatedParameter"])

    return graql_insert_query

def NotExpression_template(item):
    # NotExpression: representation of a boolean not (negation) expression
    graql_insert_query = 'insert $notexpression isa NotExpression, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ";"

    write_relationship('Reference_term', 'refersTo', 'NotExpression',
                           item["iid"], 'isReferredBy', 'BooleanExpression', item["term"])

    return graql_insert_query

def OrExpression_template(item):
    # OrExpression: representation of a boolean and (disjunction) expression
    graql_insert_query = 'insert $orexpression isa OrExpression, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ";"

    for i in item["term"]:
        write_relationship('Reference_term', 'refersTo', 'OrExpression',
                           item["iid"], 'isReferredBy', 'BooleanExpression', i)

    return graql_insert_query

def Organization_template(item):
    # Organization: simple representation of an organization
    graql_insert_query = 'insert $organization isa Organization, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    return graql_insert_query

def ParameterBase_template(item):
    # ParameterBase: abstract superclass that enables a common referencing mechanism for Parameter,
    # ParameterOverride and ParameterSubscription
    graql_insert_query = 'insert $parameterbase isa ParameterBase, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has isOptionDependent "' + str(item["isOptionDependent"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_parameterType', 'refersTo', 'ParameterBase', item["iid"],
                           'isReferredBy', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refersTo', 'ParameterBase', item["iid"],
                       'isReferredBy', 'MeasurementScale', item["scale"])

    write_relationship('Reference_owner', 'refersTo', 'ParameterBase', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["stateDependence"]:
        write_relationship('Reference_stateDependence', 'refersTo', 'ParameterBase', item["iid"],
                           'isReferredBy', 'ActualFiniteStateList', item["stateDependence"])

    if item["group"]:
        write_relationship('Reference_group', 'refersTo', 'ParameterBase', item["iid"],
                           'isReferredBy', 'ParameterGroup', item["group"])

    return graql_insert_query

def ParameterOrOverrideBase_template(item):
    # ParameterOrOverrideBase: abstract superclass to provide a common reference to Parameter and ParameterOverride
    graql_insert_query = 'insert $parameteroroverridebase isa ParameterOrOverrideBase, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has isOptionDependent "' + str(item["isOptionDependent"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_parameterType', 'refersTo', 'ParameterOrOverrideBase', item["iid"],
                       'isReferredBy', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refersTo', 'ParameterOrOverrideBase', item["iid"],
                           'isReferredBy', 'MeasurementScale', item["scale"])

    if item["stateDependence"]:
        write_relationship('Reference_stateDependence', 'refersTo', 'ParameterOrOverrideBase', item["iid"],
                           'isReferredBy', 'ActualFiniteStateList', item["stateDependence"])

    if item["group"]:
        write_relationship('Reference_group', 'refersTo', 'ParameterOrOverrideBase', item["iid"],
                           'isReferredBy', 'ParameterGroup', item["group"])

    write_relationship('Reference_owner', 'refersTo', 'ParameterOrOverrideBase', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["parameterSubscription"]:
        for i in item["parameterSubscription"]:
            write_relationship('Containment_parameterSubscription', 'contains', 'ParameterOrOverrideBase', item["iid"],
                               'isContained', 'ParameterSubscription', i)

    return graql_insert_query

def ParameterOverride_template(item):
    # ParameterOverride: representation of a parameter at ElementUsage level that allows to override the values of a
    # Parameter defined at ElementDefinition level
    graql_insert_query = 'insert $parameteroverride isa ParameterOverride, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ";"


    write_relationship('Reference_owner', 'refersTo', 'ParameterOverride', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["valueSet"]:
        for i in item["valueSet"]:
            write_relationship('Containment_valueSet', 'contains', 'ParameterOverride', item["iid"],
                               'isContained', 'ParameterOverrideValueSet', i)

    if item["parameterSubscription"]:
        for i in item["parameterSubscription"]:
            write_relationship('Containment_parameterSubscription', 'contains', 'ParameterOverride', item["iid"],
                               'isContained', 'ParameterSubscription', i)

    write_relationship('Reference_parameter', 'refersTo', 'ParameterOverride', item["iid"],
                       'isReferredBy', 'Parameter', item["parameter"])

    return graql_insert_query

def ParameterOverrideValueSet_template(item):
    # ParameterOverrideValueSet: representation of the switch setting and all values for a ParameterOverride
    graql_insert_query = 'insert $parameteroverridevalueset isa ParameterOverrideValueSet, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has valueSwitch "' + item["valueSwitch"] + '"'
    graql_insert_query += ', has computed "' + clean(item["computed"]) + '"'
    graql_insert_query += ', has manual "' + clean(item["manual"]) + '"'
    graql_insert_query += ', has reference "' + clean(item["reference"]) + '"'
    graql_insert_query += ', has published "' + clean(item["published"]) + '"'
    graql_insert_query += ', has formula "' + clean(item["formula"]) + '"'
    graql_insert_query += ";"


    write_relationship('Reference_parameterValueSet', 'refersTo', 'ParameterOverrideValueSet', item["iid"],
                       'isReferredBy', 'ParameterValueSet', item["parameterValueSet"])


    return graql_insert_query

def ParameterType_template(item):
    # ParameterType: abstract superclass that represents the common characteristics of any parameter type
    graql_insert_query = 'insert $parametertype isa ParameterType, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has numberOfValues ' + str(item["numberOfValues"])
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ParameterType',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ParameterType',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ParameterType',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'ParameterType',
                               item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def ParameterValueSetBase_template(item):
    # ParameterValueSetBase: abstract superclass representing the switch setting and values of a Parameter or
    # ParameterOverride and serves as a common reference type for ParameterValueSet and ParameterOverrideValueSet

    graql_insert_query = 'insert $parametervaluesetbase isa ParameterValueSetBase, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has valueSwitch "' + item["valueSwitch"] + '"'
    graql_insert_query += ', has computed "' + clean(item["computed"]) + '"'
    graql_insert_query += ', has manual "' + clean(item["manual"]) + '"'
    graql_insert_query += ', has reference "' + clean(item["reference"]) + '"'
    graql_insert_query += ', has actualValue "' + clean(item["actualValue"]) + '"'
    graql_insert_query += ', has published "' + clean(item["published"]) + '"'
    graql_insert_query += ', has formula "' + clean(item["formula"]) + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refersTo', 'ParameterValueSetBase', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["actualState"]:
        write_relationship('Reference_actualState', 'refersTo', 'ParameterValueSetBase', item["iid"],
                           'isReferredBy', 'ActualFiniteState', item["actualState"])

    if item["actualOption"]:
        write_relationship('Reference_actualOption', 'refersTo', 'ParameterValueSetBase', item["iid"],
                           'isReferredBy', 'Option', item["actualOption"])

    return graql_insert_query

def ParametricConstraint_template(item):
    # ParametricConstraint: representation of a single parametric constraint consisting of a ParameterType that acts
    # as a variable, a relational operator and a value, in the form of a mathematical equality or inequality
    graql_insert_query = 'insert $parametricconstraint isa ParametricConstraint, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ";"


    if item["topExpression"]:
        write_relationship('Reference_topExpression', 'refersTo', 'ParametricConstraint',
                           item["iid"],
                           'isReferredBy', 'BooleanExpression', item["topExpression"])

    write_relationship('Reference_owner', 'refersTo', 'ParametricConstraint', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    for i in item["expression"]:
        write_relationship('Containment_expression', 'contains', 'ParametricConstraint',
                           item["iid"], 'isContained', 'BooleanExpression', i)


    return graql_insert_query

# -----------------------------

def ParticipantPermission_template(item):
    # ParticipantPermission: representation of a permission to access a given (sub)set of data in an EngineeringModel
    graql_insert_query = 'insert $participantpermission isa ParticipantPermission, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has accessRight "' + item["accessRight"] + '"'
    graql_insert_query += ', has objectClass "' + item["objectClass"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"


    return graql_insert_query

def ParticipantRole_template(item):
    # ParticipantRole: representation of the named role of a Participant that defines the Participant's permissions
    # and access rights with respect to data in an EngineeringModel
    graql_insert_query = 'insert $participantrole isa ParticipantRole, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ParticipantRole',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ParticipantRole',
                               item["iid"],
                               'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ParticipantRole',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["participantPermission"]:
        for i in item["participantPermission"]:
            write_relationship('Containment_participantPermission', 'contains', 'ParticipantRole',
                               item["iid"], 'isContained', 'ParticipantPermission', i)

    return graql_insert_query

def PersonPermission_template(item):
    # PersonPermission: representation of a permission to access a given (sub)set of data in a SiteDirectory
    graql_insert_query = 'insert $personpermission isa PersonPermission, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has accessRight "' + item["accessRight"] + '"'
    graql_insert_query += ', has objectClass "' + item["objectClass"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    return graql_insert_query

def PersonRole_template(item):
    # PersonRole: representation of the named role of a Person (a user) that defines the Person's permissions and
    # access rights with respect to data in a SiteDirectory
    graql_insert_query = 'insert $personrole isa PersonRole, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'PersonRole',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'PersonRole',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'PersonRole',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["personPermission"]:
        for i in item["personPermission"]:
            write_relationship('Containment_personPermission', 'contains', 'PersonRole',
                               item["iid"], 'isContained', 'PersonPermission', i)

    return graql_insert_query

def PossibleFiniteState_template(item):
    # PossibleFiniteState: representation of one of the finite states of a PossibleFiniteStateList
    graql_insert_query = 'insert $possiblefinitestate isa PossibleFiniteState, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'PossibleFiniteState',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'PossibleFiniteState',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'PossibleFiniteState',
                               item["iid"], 'isContained', 'HyperLink', i)
    #ToDo
    # if item['owner']:
    #     for i in item["owner"]:
    #         write_relationship('Reference_owner', 'refersTo', 'PossibleFiniteState', item["iid"],
    #                        'isReferredBy', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def PossibleFiniteStateList_template(item):
    # PossibleFiniteStateList: specialization of CategorizableThing that defines a finite ordered collection of
    # one or more named States
    graql_insert_query = 'insert $possiblefinitestatelist isa PossibleFiniteStateList, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'PossibleFiniteStateList',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'PossibleFiniteStateList',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'PossibleFiniteStateList',
                               item["iid"], 'isContained', 'HyperLink', i)

    write_relationship('Reference_owner', 'refersTo', 'PossibleFiniteStateList', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    for i in item["possibleState"]:
        write_relationship('Containment_possibleState', 'contains', 'PossibleFiniteStateList', item["iid"],
                           'isContained', 'PossibleFiniteState', i['v'])

    if item["defaultState"]:
        write_relationship('Reference_defaultState', 'refersTo', 'PossibleFiniteStateList',
                           item["iid"], 'isReferredBy', 'PossibleFiniteState', item["defaultState"])

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'PossibleFiniteStateList',
                               item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def QuantityKind_template(item):
    # QuantityKind: representation of a numerical ScalarParameterType
    graql_insert_query = 'insert $quantitykind isa QuantityKind, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has numberOfValues ' + str(item["numberOfValues"])
    graql_insert_query += ', has quantityDimensionExpression "' + item["quantityDimensionExpression"] + '"'
    if item["quantityDimensionSymbol"]:
        graql_insert_query += ', has quantityDimensionSymbol "' + item["quantityDimensionSymbol"] + '"'
    if item["quantityDimensionExponent"]:
        combined = ''
        for i in item["quantityDimensionExponent"]:
            combined += clean(i) + ' ,'
        graql_insert_query += ', hasq uantityDimensionExponent "' + combined + '"'

    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'QuantityKind',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'QuantityKind',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'QuantityKind',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'QuantityKind',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["possibleScale"]:
        for i in item["possibleScale"]:
            write_relationship('Reference_possibleScale', 'refersTo', 'QuantityKind',
                               item["iid"], 'isReferredBy', 'MeasurementScale', i)

    write_relationship('Reference_defaultScale', 'refersTo', 'SpecializedQuantityKind',
                       item["iid"], 'isReferredBy', 'MeasurementScale', item["defaultScale"])

    if item["allPossibleScale"]:
        for i in item["allPossibleScale"]:
            write_relationship('Reference_allPossibleScale', 'refersTo', 'QuantityKind',
                               item["iid"], 'isReferredBy', 'MeasurementScale', i)

    return graql_insert_query

def ReferenceDataLibrary_template(item):
    # ReferenceDataLibrary: named library that holds a set of (predefined) reference data that can be loaded at runtime
    # and used in an EngineeringModel
    graql_insert_query = 'insert $referencedatalibrary isa ReferenceDataLibrary, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ReferenceDataLibrary',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ReferenceDataLibrary',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ReferenceDataLibrary',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["definedCategory"]:
        for i in item["definedCategory"]:
            write_relationship('Containment_definedCategory', 'contains', 'ReferenceDataLibrary',
                               item["iid"], 'isContained', 'Category', i)

    if item["parameterType"]:
        for i in item["parameterType"]:
            write_relationship('Containment_parameterType', 'contains', 'ReferenceDataLibrary',
                               item["iid"], 'isContained', 'ParameterType', i)

    if item["scale"]:
        for i in item["scale"]:
            write_relationship('Containment_scale', 'contains', 'ReferenceDataLibrary',
                               item["iid"], 'isContained', 'MeasurementScale', i)

    if item["unitPrefix"]:
        for i in item["unitPrefix"]:
            write_relationship('Containment_unitPrefix', 'contains', 'ReferenceDataLibrary',
                               item["iid"], 'isContained', 'UnitPrefix', i)

    if item["unit"]:
        for i in item["unit"]:
            write_relationship('Containment_unit', 'contains', 'ReferenceDataLibrary',
                               item["iid"], 'isContained', 'MeasurementUnit', i)

    if item["fileType"]:
        for i in item["fileType"]:
            write_relationship('Containment_fileType', 'contains', 'ReferenceDataLibrary',
                               item["iid"], 'isContained', 'FileType', i)

    if item["glossary"]:
        for i in item["glossary"]:
            write_relationship('Containment_glossary', 'contains', 'ReferenceDataLibrary',
                               item["iid"], 'isContained', 'Glossary', i)

    if item["referenceSource"]:
        for i in item["referenceSource"]:
            write_relationship('Containment_referenceSource', 'contains', 'ReferenceDataLibrary',
                               item["iid"], 'isContained', 'ReferenceSource', i)

    if item["rule"]:
        for i in item["rule"]:
            write_relationship('Containment_rule', 'contains', 'ReferenceDataLibrary',
                               item["iid"], 'isContained', 'Rule', i)

    if item["constant"]:
        for i in item["constant"]:
            write_relationship('Containment_constant', 'contains', 'ReferenceDataLibrary',
                               item["iid"], 'isContained', 'Constant', i)

    if item["baseQuantityKind"]:
        for i in item["baseQuantityKind"]:
            write_relationship('Reference_baseQuantityKind', 'refersTo', 'ReferenceDataLibrary',
                               item["iid"], 'isReferredBy', 'QuantityKind', i["v"])

    if item["baseUnit"]:
        for i in item["baseUnit"]:
            write_relationship('Reference_baseUnit', 'refersTo', 'ReferenceDataLibrary',
                               item["iid"], 'isReferredBy', 'MeasurementUnit', i)

    if item["requiredRdl"]:
        write_relationship('Reference_requiredRdl', 'refersTo', 'ReferenceDataLibrary',
                           item["iid"], 'isReferredBy', 'SiteReferenceDataLibrary', item["requiredRdl"])

    return graql_insert_query

def ReferencerRule_template(item):
    # ReferencerRule: representation of a validation rule for ElementDefinitions and the
    # referencedElement NestedElements
    graql_insert_query = 'insert $referencerrule isa ReferencerRule, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has minReferenced ' + str(item["minReferenced"])
    graql_insert_query += ', has maxReferenced ' + str(item["maxReferenced"])
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ReferencerRule',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ReferencerRule',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ReferencerRule',
                               item["iid"], 'isContained', 'HyperLink', i)

    write_relationship('Reference_referencingCategory', 'refersTo', 'ReferencerRule',
                       item["iid"], 'isReferredBy', 'Category', item["referencingCategory"])

    for i in item["referencedCategory"]:
        write_relationship('Reference_referencedCategory', 'refersTo', 'ReferencerRule',
                           item["iid"], 'isReferredBy', 'Category', i)

    return graql_insert_query

def RelationalExpression_template(item):
    # RelationalExpression: representation of a mathematical equality or inequality defined by a ParameterType
    # that acts as a variable, a relational operator and a v
    graql_insert_query = 'insert $relationalexpression isa RelationalExpression, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has value "' + item["value"] + '"'
    graql_insert_query += ', has relationalOperator "' + item["relationalOperator"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_parameterType', 'refersTo', 'RelationalExpression', item["iid"],
                       'isReferredBy', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refersTo', 'RelationalExpression', item["iid"],
                           'isReferredBy', 'MeasurementScale', item["scale"])

    return graql_insert_query

def Relationship_template(item):
    # Relationship: representation of a relationship between two or more Things
    graql_insert_query = 'insert $relationship isa Relationship, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ";"

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'Relationship',
                               item["iid"], 'isReferredBy', 'Category', i)

    write_relationship('Reference_owner', 'refersTo', 'Relationship', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def Requirement_template(item):
    # Requirement: representation of a requirement in a RequirementsSpecification
    graql_insert_query = 'insert $requirement isa Requirement, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'Requirement',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'Requirement',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'Requirement',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["group"]:
        write_relationship('Reference_group', 'refersTo', 'Requirement', item["iid"],
                           'isReferredBy', 'ParameterGroup', item["group"])

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'Requirement',
                               item["iid"], 'isReferredBy', 'Category', i)

    write_relationship('Reference_owner', 'refersTo', 'Requirement', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["parametricConstraint"]:
        for i in item["parametricConstraint"]:
            write_relationship('Containment_parametricConstraint', 'contains', 'Requirement',
                               item["iid"], 'isContained', 'ParametricConstraint', i)

    if item["parameterValue"]:
        for i in item["parameterValue"]:
            write_relationship('Containment_parameterValue', 'contains', 'Requirement',
                               item["iid"], 'isContained', 'SimpleParameterValue', i)

    return graql_insert_query

def RequirementsContainer_template(item):
    # RequirementsContainer: abstract superclass that serves as a common reference to both RequirementsSpecification
    # and RequirementsGroup
    graql_insert_query = 'insert $requirementscontainer isa RequirementsContainer, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'RequirementsContainer',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'RequirementsContainer',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'RequirementsContainer',
                               item["iid"], 'isContained', 'HyperLink', i)

    write_relationship('Reference_owner', 'refersTo', 'RequirementsContainer', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["group"]:
        for i in item["group"]:
            write_relationship('Containment_group', 'contains', 'RequirementsContainer',
                               item["iid"], 'isContained', 'RequirementsGroup', i)

    return graql_insert_query

def RequirementsGroup_template(item):
    # RequirementsGroup: representation of a grouping of Requirements
    graql_insert_query = 'insert $requirementsgroup isa RequirementsGroup, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'RequirementsGroup',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'RequirementsGroup',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'RequirementsGroup',
                               item["iid"], 'isContained', 'HyperLink', i)

    write_relationship('Reference_owner', 'refersTo', 'RequirementsGroup', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["group"]:
        for i in item["group"]:
            write_relationship('Containment_group', 'contains', 'RequirementsGroup',
                               item["iid"], 'isContained', 'RequirementsGroup', i)

    return graql_insert_query

def Rule_template(item):
    # Rule: representation of a validation or constraint rule for CategorizableThings and relations between them
    graql_insert_query = 'insert $rule isa Rule, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'Rule',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'Rule',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'Rule',
                               item["iid"], 'isContained', 'HyperLink', i)

    return graql_insert_query

def RuleVerification_template(item):
    # RuleVerification: representation of built-in data model rule or user-defined Rule to be verified and
    # its current verification result
    graql_insert_query = 'insert $ruleverification isa RuleVerification, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has isActive "' + str(item["isActive"]) + '"'
    if item["executedOn"]:
        graql_insert_query += ', has executedOn "' + item["executedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has status "' + item["status"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refersTo', 'RuleVerification', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["violation"]:
        for i in item["violation"]:
            write_relationship('Containment_violation', 'contains', 'RuleVerification',
                               item["iid"], 'isContained', 'RuleViolation', i)

    return graql_insert_query

def RuleVerificationList_template(item):
    # RuleVerificationList: representation of a list of RuleVerifications
    graql_insert_query = 'insert $ruleverificationlist isa RuleVerificationList, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'RuleVerificationList',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'RuleVerificationList',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'RuleVerificationList',
                               item["iid"], 'isContained', 'HyperLink', i)

    write_relationship('Reference_owner', 'refersTo', 'RuleVerificationList', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["ruleVerification"]:
        for i in item["ruleVerification"]:
            write_relationship('Containment_ruleVerification', 'contains', 'RuleVerificationList',
                               item["iid"], 'isContained', 'RuleVerification', i)

    return graql_insert_query

def RuleViolation_template(item):
    # RuleViolation: representing of information concerning the violation of a built-in or user-defined rule
    graql_insert_query = 'insert $ruleviolation isa RuleViolation, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has description "' + item["description"] + '"'

    if item["violatingThing"]:
        # Combine all notes into 1 as Grakn only accepts one instance of one attribute
        combined = ''
        for i in item["violatingThing"]:
            combined += clean(i) + ' ,'
        graql_insert_query += ', has violatingThing "' + combined + '"'

    graql_insert_query += ";"

    return graql_insert_query

def ScalarParameterType_template(item):
    # ScalarParameterType: representation of a scalar parameter type
    graql_insert_query = 'insert $scalarparametertype isa ScalarParameterType, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has symbol "' + item["symbol"] + '"'
    graql_insert_query += ', has isDeprecated "' + str(item["isDeprecated"]) + '"'
    graql_insert_query += ', has numberOfValues ' + str(item["numberOfValues"])
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'ScalarParameterType',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'ScalarParameterType',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'ScalarParameterType',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'ScalarParameterType',
                               item["iid"], 'isReferredBy', 'Category', i)
    return graql_insert_query

def SimpleParameterValue_template(item):
    # SimpleParameterValue: representation of a single parameter with value for a SimpleParameterizableThing
    graql_insert_query = 'insert $simpleparametervalue isa SimpleParameterValue, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has value "' + item["value"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_parameterType', 'refersTo', 'SimpleParameterValue', item["iid"],
                       'isReferredBy', 'ParameterType', item["parameterType"])

    if item["scale"]:
        write_relationship('Reference_scale', 'refersTo', 'SimpleParameterValue', item["iid"],
                           'isReferredBy', 'MeasurementScale', item["scale"])

    write_relationship('Reference_owner', 'refersTo', 'SimpleParameterValue', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def SimpleParameterizableThing_template(item):
    # SimpleParameterizableThing: representation of a Thing that can be characterized by one or
    # more parameters with values
    graql_insert_query = 'insert $simpleparameterizablething isa SimpleParameterizableThing, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ";"

    if item["alias"]:
        for i in item["alias"]:
            write_relationship('Containment_alias', 'contains', 'SimpleParameterizableThing',
                               item["iid"], 'isContained', 'Alias', i)

    if item["definition"]:
        for i in item["definition"]:
            write_relationship('Containment_definition', 'contains', 'SimpleParameterizableThing',
                               item["iid"], 'isContained', 'Definition', i)

    if item["hyperLink"]:
        for i in item["hyperLink"]:
            write_relationship('Containment_hyperLink', 'contains', 'SimpleParameterizableThing',
                               item["iid"], 'isContained', 'HyperLink', i)

    if item["parameterValue"]:
        for i in item["parameterValue"]:
            write_relationship('Containment_parameterValue', 'contains', 'SimpleParameterizableThing',
                               item["iid"], 'isContained', 'SimpleParameterValue', i)

    write_relationship('Reference_owner', 'refersTo', 'SimpleParameterizableThing', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    return graql_insert_query

def SiteLogEntry_template(item):
    # SiteLogEntry: representation of a logbook entry for a SiteDirectory
    graql_insert_query = 'insert $sitelogentry isa SiteLogEntry, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has languageCode "' + item["languageCode"] + '"'
    graql_insert_query += ', has content "' + item["content"] + '"'
    graql_insert_query += ', has createdOn "' + item["createdOn"] + '"'
    graql_insert_query += ', has level "' + item["level"] + '"'

    if item["affectedItemIid"]:
        # Combine all notes into 1
        combined=''
        for i in item["affectedItemIid"]:
            combined += i + ' ,'
        graql_insert_query += ', has affectedItemIid "' + combined + '"'

    graql_insert_query += ";"

    if item["category"]:
        for i in item["category"]:
            write_relationship('Reference_category', 'refersTo', 'SiteLogEntry',
                               item["iid"], 'isReferredBy', 'Category', i)

    if item["author"]:
        write_relationship('Reference_author', 'refersTo', 'SiteLogEntry',
                           item["iid"], 'isReferredBy', 'Person', item["author"])
    return graql_insert_query

def TelephoneNumber_template(item):
    # TelephoneNumber: representation of a telephone number
    graql_insert_query = 'insert $telephoneNumber isa TelephoneNumber, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has vcardType "' + item["vcardType"][0] + '"'
    graql_insert_query += ', has value "' + item["value"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

def TopContainer_template(item):
    # TopContainer: representation of a top container
    graql_insert_query = 'insert $topcontainer isa TopContainer, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] + '", has lastModifiedOn "' + item["modifiedOn"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

def UserPreference_template(item):
    # UserPreference: representation of a user-defined preference
    graql_insert_query = 'insert $userpreference isa UserPreference, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has shortName "' + item["shortName"] + '"'
    graql_insert_query += ', has value "' + item["value"] + '"'
    graql_insert_query += ";"

    return graql_insert_query

def UserRuleVerification_template(item):
    # UserRuleVerification: representation of the verification of a user-defined Rule in one of
    # the required ReferenceDataLibraries
    graql_insert_query = 'insert $userruleverification isa UserRuleVerification, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ', has isActive "' + str(item["isActive"]) + '"'
    if item["executedOn"]:
        graql_insert_query += ', has executedOn "' + item["executedOn"] + '"'
    graql_insert_query += ', has name "' + item["name"] + '"'
    graql_insert_query += ', has status "' + item["status"] + '"'
    graql_insert_query += ";"

    write_relationship('Reference_owner', 'refersTo', 'UserRuleVerification', item["iid"],
                       'isReferredBy', 'DomainOfExpertise', item["owner"])

    if item["violation"]:
        for i in item["violation"]:
            write_relationship('Containment_violation', 'contains', 'UserRuleVerification',
                               item["iid"], 'isContained', 'RuleViolation', i)

    write_relationship('Reference_rule', 'refersTo', 'UserRuleVerification', item["iid"],
                       'isReferredBy', 'Rule', item["rule"])


    return graql_insert_query

def Thing_template(item):
    # Thing: top level abstract superclass from which all domain concept classes in the model inherit
    graql_insert_query = 'insert $thing isa Thing, has revisionNumber "' + \
                         str(item["revisionNumber"]) + '", has classKind "' + item["classKind"] + \
                         '", has id "' + item["iid"] +  '"'
    graql_insert_query += ";"

    return graql_insert_query

# -------------------------------------------------------------
# END
# -------------------------------------------------------------

