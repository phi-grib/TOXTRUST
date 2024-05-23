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
    e.combinationRule(rule)
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


def returnEvidenceResult(endpointName, id : str, selection = None): #id
    
    e = Endpoint(endpointName)
    e.load()
    
    return e.returnResult(id , selection)
    

def runCombine(endpointName): #pass should combine
    
    e = Endpoint(endpointName)
    
    e.load()
    e.runCombination()
    e.save()


def runDecision(endpointName, id : str): 

    e = Endpoint(endpointName)
