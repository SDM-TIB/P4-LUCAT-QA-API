#!/usr/bin/env python3
#
# Description: POST service for exploration of
# data of Lung Cancer in the iASiS KG.
#

import sys
import os
from flask import Flask, abort, request, make_response
import json
from SPARQLWrapper import SPARQLWrapper, JSON
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

LIMIT=10

#KG="http://node2.research.tib.eu:18875/sparql"
KG = os.environ["ENDPOINT"]
#KG="https://labs.tib.eu/sdm/p4lucat_kg/sparql"

#
#KG="http://node2.research.tib.eu:18881/sparql"
EMPTY_JSON = "{}"

app = Flask(__name__)



############################
#
# Query generation
#
############################


def execute_query(query):
    sparql_ins = SPARQLWrapper(KG)
    sparql_ins.setQuery(query)
    sparql_ins.setReturnFormat(JSON)
    return sparql_ins.query().convert()['results']['bindings']



############################
#
# Processing results
#
############################

def cui2drugs(cui,finalresult):
    query="""select distinct ?dlabel ?phlabel where {
                        ?d a <http://research.tib.eu/p4-lucat/vocab/Drug>.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?dlabel.
                         ?d ?p ?o.
                         ?ph a <http://research.tib.eu/p4-lucat/vocab/Phenotype>.
                         ?ph ?p2 ?o.
                         ?ph <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                         ?ph <http://research.tib.eu/p4-lucat/vocab/phenotypeLabel> ?phlabel.  
                         FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
}
    """

    #print (query)
    qresults = execute_query(query)
    #print(qresults)
    #finalresult=dict()
    for result in qresults:
        item={}
        item["Subject"]=result["dlabel"]["value"].replace("_"," ")
        item["Relation"]="Side Effect"
        item["Object"]=result["phlabel"]["value"].replace("_"," ")
        finalresult.append(item)
        
        
    query="""select distinct ?dlabel ?p ?d2label where {
{
                        ?d a <http://research.tib.eu/p4-lucat/vocab/Drug>.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?dlabel.
                        ?s ?p ?d.
                        ?s <http://research.tib.eu/p4-lucat/vocab/isAffected> ?d2.
                        ?d2 <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?d2label.
                        ?d2 <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                        FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
} 
UNION
{
                        ?d a <http://research.tib.eu/p4-lucat/vocab/Drug>.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?dlabel.
                        ?s ?p ?d.
                        ?s <http://research.tib.eu/p4-lucat/vocab/affects> ?d2.
                        ?d2 <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?d2label.
                        ?d2 <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                        FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
}
UNION
{
                        ?d a <http://research.tib.eu/p4-lucat/vocab/Drug>.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?dlabel.
                        ?s ?p ?d.
                        ?s <http://research.tib.eu/p4-lucat/vocab/interactor1_Drug> ?d2.
                        ?d2 <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?d2label.
                        ?d2 <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                        FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
}
UNION
{
                        ?d a <http://research.tib.eu/p4-lucat/vocab/Drug>.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?dlabel.
                        ?s ?p ?d.
                        ?s <http://research.tib.eu/p4-lucat/vocab/interactor2_Drug> ?d2.
                        ?d2 <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?d2label.
                        ?d2 <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                        FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
}
UNION
{
                        ?d a <http://research.tib.eu/p4-lucat/vocab/Drug>.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?dlabel.
                        ?s ?p ?d.
                        ?s <http://research.tib.eu/p4-lucat/vocab/biomarkerLabel> ?d2label.
                        ?s <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                        FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))


}
UNION
{
                        ?d a <http://research.tib.eu/p4-lucat/vocab/Drug>.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?dlabel.
                        ?s ?p ?d.
                        ?s <http://research.tib.eu/p4-lucat/vocab/tumorStageLabel> ?d2label.
                        ?s <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                        FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))


}                      
}
    """

    #print (query)
    qresults = execute_query(query)
    for result in qresults:
        item={}
        item["Subject"]=result["d2label"]["value"].replace("_"," ")
        item["Relation"]=result["p"]["value"].replace("http://research.tib.eu/p4-lucat/vocab/","").replace("_"," ")
        if item["Relation"]=="interactor1":
            item["Relation"]="drugDrugPrediction_Interactor1"
        elif item["Relation"]=="interactor2":
            item["Relation"]="drugDrugPrediction_Interactor2"
        item["Object"]=result["dlabel"]["value"].replace("_"," ")
        finalresult.append(item)
        
    return finalresult


def cui2disorders(cui,finalresult):
    query="""select distinct ?d2label  ?dlabel where
{
{
                        ?d a <http://research.tib.eu/p4-lucat/vocab/Disorder>.
                        ?d <http://research.tib.eu/p4-lucat/vocab/disorderLabel> ?dlabel.
                        ?s ?p ?d.
                        ?s <http://research.tib.eu/p4-lucat/vocab/interactor1_Drug> ?d2.
                        ?d2 <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?d2label.
                        ?d2 <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                         FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
}
UNION
{
                        ?d a <http://research.tib.eu/p4-lucat/vocab/Disorder>.
                        ?d <http://research.tib.eu/p4-lucat/vocab/disorderLabel> ?dlabel.
                        ?s ?p ?d.
                        ?s <http://research.tib.eu/p4-lucat/vocab/interactor1_Drug> ?d2.
                        ?d2 <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?d2label.
                        ?d <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                         FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
}
}
    """

    #print (query)
    qresults = execute_query(query)
    #print(qresults)
    #finalresult=dict()
    for result in qresults:
        item={}
        item["Subject"]=result["d2label"]["value"].replace("_"," ")
        item["Relation"]="Drug Disorder"
        item["Object"]=result["dlabel"]["value"].replace("_"," ")
        finalresult.append(item)
        
 
    return finalresult


def cui2phenotype(cui,finalresult):
    query="""select distinct ?phlabel ?p ?dlabel where 
    {
    {  
                        ?ph a <http://research.tib.eu/p4-lucat/vocab/Phenotype>.
                        ?ph <http://research.tib.eu/p4-lucat/vocab/toxicityLabel_ENG> ?phlabel.
                        ?ph ?p ?o.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drug_isRelatedTo_dse> ?o.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?dlabel.
                        ?d <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                         FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
}
    UNION
    {
                         ?ph a <http://research.tib.eu/p4-lucat/vocab/Phenotype>.
                        ?ph <http://research.tib.eu/p4-lucat/vocab/toxicityLabel_ENG> ?phlabel.
                        ?ph ?p ?o.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drug_isRelatedTo_dse> ?o.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?dlabel.
                        ?ph <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                         FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))   
    }
    }
    """

    #print (query)
    qresults = execute_query(query)
    #print(qresults)
    #finalresult=dict()
    for result in qresults:
        item={}
        item["Subject"]=result["phlabel"]["value"].replace("_"," ")
        item["Relation"]="drugSideEffectInteraction"
        item["Object"]=result["dlabel"]["value"].replace("_"," ")
        finalresult.append(item)
        
 
    return finalresult

def cui2protein(cui,finalresult):
    query="""select distinct ?tlabel ?p ?glabel where 
    {
    {
                        ?t a <http://research.tib.eu/p4-lucat/vocab/Target>.
                        ?t <http://research.tib.eu/p4-lucat/vocab/targetLabel> ?tlabel.
                        ?t ?p ?o.
                        ?o a <http://research.tib.eu/p4-lucat/vocab/Gene>.
                        ?o <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                        ?cui <http://research.tib.eu/p4-lucat/vocab/annLabel> ?glabel.
                         FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
}
    UNION
    {
                         ?t a <http://research.tib.eu/p4-lucat/vocab/Target>.
                        ?t <http://research.tib.eu/p4-lucat/vocab/targetLabel> ?tlabel.
                        ?t ?p ?o.
                        ?o a <http://research.tib.eu/p4-lucat/vocab/Gene>.
                        ?t <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                        ?cui <http://research.tib.eu/p4-lucat/vocab/annLabel> ?glabel.
                         FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
    }
    }
    """

    #print (query)
    qresults = execute_query(query)
    #print(qresults)
    #finalresult=dict()
    for result in qresults:
        item={}
        item["Subject"]=result["tlabel"]["value"].replace("_"," ")
        item["Relation"]=result["p"]["value"].replace("http://research.tib.eu/p4-lucat/vocab/","").replace("_"," ")
        item["Object"]=result["glabel"]["value"].replace("_"," ")
        finalresult.append(item)
        
        
        
    query="""select distinct ?tlabel ?p ?dlabel where 
    {
    {
                        ?t a <http://research.tib.eu/p4-lucat/vocab/Target>.
                        ?t rdfs:label ?tlabel.
                        ?o ?p ?t.
                        ?o <http://research.tib.eu/p4-lucat/vocab/interactor1_Drug> ?d.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?dlabel.
                        ?d <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                         FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
}
    UNION
    {
                            ?t a <http://research.tib.eu/p4-lucat/vocab/Target>.
                        ?t rdfs:label ?tlabel.
                        ?o ?p ?t.
                        ?o <http://research.tib.eu/p4-lucat/vocab/interactor1_Drug> ?d.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?dlabel.
                        ?t <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                         FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
    }
    }
    """

    #print (query)
    qresults = execute_query(query)
    #print(qresults)
    #finalresult=dict()
    for result in qresults:
        item={}
        item["Subject"]=result["tlabel"]["value"].replace("_"," ")
        item["Relation"]="drugTargetInteraction"
        item["Object"]=result["dlabel"]["value"].replace("_"," ")
        finalresult.append(item)
        
 
    return finalresult


def cui2enzyme(cui,finalresult):
    query="""select distinct ?p ?e ?glabel where 
    {
    {
                        ?e a <http://research.tib.eu/p4-lucat/vocab/Enzyme>.
                        ?e ?p ?o.
                        ?o a <http://research.tib.eu/p4-lucat/vocab/Gene>.
                        ?o <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                        ?cui <http://research.tib.eu/p4-lucat/vocab/annLabel> ?glabel.
                        ?d <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                         FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
}
    UNION
    {
                         ?e a <http://research.tib.eu/p4-lucat/vocab/Enzyme>.
                        ?e ?p ?o.
                        ?o a <http://research.tib.eu/p4-lucat/vocab/Gene>.
                        ?e <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                        ?cui <http://research.tib.eu/p4-lucat/vocab/annLabel> ?glabel.
                        ?d <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                         FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
    }
    }
    """

    #print (query)
    qresults = execute_query(query)
    #print(qresults)
    #finalresult=dict()
    for result in qresults:
        item={}
        item["Subject"]=result["e"]["value"].replace("http://research.tib.eu/p4-lucat/entity/","").replace("_"," ")
        item["Relation"]=result["p"]["value"].replace("http://research.tib.eu/p4-lucat/vocab/","").replace("_"," ")
        item["Object"]=result["glabel"]["value"].replace("http://research.tib.eu/p4-lucat/entity/","").replace("_"," ")
        finalresult.append(item)
        
        
        
    query="""select distinct ?e ?p ?dlabel where {
                        ?e a <http://research.tib.eu/p4-lucat/vocab/Enzyme>.
                        ?o ?p ?e.
                        ?o <http://research.tib.eu/p4-lucat/vocab/interactor1_Drug> ?d.
                        ?d <http://research.tib.eu/p4-lucat/vocab/drugLabel> ?dlabel.
                        ?d <http://research.tib.eu/p4-lucat/vocab/hasCUIAnnotation> ?cui.
                         FILTER (?cui in (<http://research.tib.eu/p4-lucat/entity/"""+cui+""">))
}
    """

    #print (query)
    qresults = execute_query(query)
    #print(qresults)
    #finalresult=dict()
    for result in qresults:
        item={}
        item["Subject"]=result["e"]["value"].replace("http://research.tib.eu/p4-lucat/entity/","").replace("_"," ")
        item["Relation"]="drugEnzymeInteraction"
        item["Object"]=result["dlabel"]["value"].replace("http://research.tib.eu/p4-lucat/entity/","").replace("_"," ")
        finalresult.append(item)
        
 
    return finalresult

def proccesing_response(input_dicc):
    finalResponse = {}
    drugs=[]
    disorders=[]
    phenotypes=[]
    #proteins=[]
    enzymes=[]
    
    for cui in input_dicc["cuis"]:
        
        drugs=cui2drugs(cui,drugs)
        disorders=cui2disorders(cui,disorders)
        phenotypes=cui2phenotype(cui,phenotypes)
       # proteins=cui2protein(cui,proteins)
        enzymes=cui2enzyme(cui,enzymes)
        
        
        
        
        #drugs.extend(drugs_result)
        #disorders.extend(disorders_result)
        #phenotypes.extend(phenotypes_result)
        #proteins.extend(proteins_result)
        #enzymes.extend(enzymes_result)
        
        
      
     
    finalResponse["drugs"]=drugs
    finalResponse["disorders"]=disorders
    finalResponse["phenotypes"]=phenotypes
   # finalResponse["proteins"]=proteins
    finalResponse["enzymes"]=enzymes
    return finalResponse





@app.route('/qa_cui_service', methods=['POST'])
def run_exploration_api():
    if (not request.json):
        abort(400)
    

    input_list = request.json
    if len(input_list) == 0:
        logger.info("Error in the input format")
        r = "{results: 'Error in the input format'}"
    else:
        response = proccesing_response(input_list)
        r = json.dumps(response, indent=4)            
    logger.info("Sending the results: ")
    response = make_response(r, 200)
    response.mimetype = "application/json"
    return response

def main(*args):
    if len(args) == 1:
        myhost = args[0]
    else:
        myhost = "0.0.0.0"
    app.run(debug=False, host=myhost)
    
if __name__ == '__main__':
     main(*sys.argv[1:])