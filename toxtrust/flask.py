import os
import yaml
import string

from toxtrust.endpoint import Endpoint

def callEndpointInput(endpointName, userEndpoint: dict):
    
    e = Endpoint(endpointName)
    
    e.load()
    e.endpointInput(userEndpoint)
    e.save()

def callEvidenceInput(endpointName, id : str, userEvidence : dict):
    
    # dump user input into yaml
    
    e = Endpoint(endpointName)
    
    e.load()
    e.evidenceInput(id, userEvidence)
    e.save()
    

def callDecisionInput(endpointName, userDecision : dict):   #### ask whether the user wants to keep defaults or not
    
    # dump config for decisions into yaml 
    
    e = Endpoint(endpointName)
    
    e.load()
    e.decisionInput(userDecision)
    e.save()

def selectRule(endpointName, rule = 'auto'):
    
    e = Endpoint(endpointName)
    
    e.load()
    e.decisionInput(rule)
    e.save()

def callCombinationInput(endpointName, combinationDict: dict):    # combinationDict = {'inagakiScale': 0.5, 'maxUncertainty': 0.3,'woe' : False}
    
    # dump config for combination into yaml 
    
    e = Endpoint(endpointName)
    
    e.load()
    e.combinationInput(combinationDict)
    e.save()


def shouldCombineInput(endpointName, shouldCombine: list):
    
    # dump ids into yaml
    
    e = Endpoint(endpointName)
    
    e.load()
    e.shoudCombine(shouldCombine)
    e.save()


def runEvidence(): #id
    
    
    # check if id in user input
    # pass data to class Evidence
    # compute
    # add results to yaml
        # evidence [id] = instance.evidence
        # results['evidence'] = instance.decision
    
    pass 

def runCombine(should_combine: list): #pass should combine
    pass

def runDecision(): 

    pass
