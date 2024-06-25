
from toxtrust.endpoint import Endpoint

def callEndpointInput(endpointName, userEndpoint: dict):
    
    e = Endpoint(endpointName)
    
    e.load()
    e.endpointInput(userEndpoint)
    e.save()
    
    return True, f'Data for endpoint {endpointName} successfully saved'

def callEvidenceInput(endpointName, id : str, userEvidence : dict):
    
    # dump user input into yaml
    
    e = Endpoint(endpointName)
    
    e.load()
    e.evidenceInput(id, userEvidence)
    e.save()
    
    return True, f'Evidence {id} for endpoint {endpointName} successfully saved'

def callDecisionInput(endpointName, userDecision : dict):   #### ask whether the user wants to keep defaults or not
    
    # dump config for decisions into yaml 
    
    e = Endpoint(endpointName)
    
    e.load()
    e.decisionInput(userDecision)
    e.save()
    
    return True, f'Decision settings successfully saved for endpoint {endpointName}'

def selectRule(endpointName, rule = 'auto'):
    
    e = Endpoint(endpointName)
    
    e.load()
    e.combinationRule(rule)
    e.save()
    
    return True, f'{rule} rule selected for endpoint {endpointName}'

def callCombinationInput(endpointName, combinationDict: dict):    # combinationDict = {'inagakiScale': 0.5, 'maxUncertainty': 0.3,'woe' : False}
    
    # dump config for combination into yaml 
    
    e = Endpoint(endpointName)
    
    e.load()
    e.combinationInput(combinationDict)
    e.save()
    
    return True, f'Combination options for endpoint {endpointName} successfully saved'

def shouldCombineInput(endpointName, shouldCombine: list):
    
    # dump ids into yaml
    
    e = Endpoint(endpointName)
    
    e.load()
    e.shoudCombine(shouldCombine)
    e.save()

    return True, f'Evidence pieces for combination successfully saved for endpoint {endpointName}'

def returnEvidenceResult(endpointName, id : str, selection = None): #id
    
    e = Endpoint(endpointName)
    e.load()
    
    return e.returnResult(id , selection)
    

def runCombine(endpointName): #pass should combine
    
    e = Endpoint(endpointName)
    
    e.load()
    e.runCombination()
    e.save()
    
    return True, f'Evidence pieces successfully combined for endpoint {endpointName}'
    
def returnCombination(endpointName):
        
    e = Endpoint(endpointName)
    
    e.load()
    return e.results['combination']

def runDecision(endpointName, id = 'combination'): 

    e = Endpoint(endpointName)
    
    e.load()
    e.makeDecision(id)
    e.save()
    
    return True, f'Decision successfully made for evidence {id} for endpoint {endpointName}'
    
#def returnDecision(endpointName, id: str):
#    
#    e = Endpoint(endpointName)
#    
#    e.load()
#    
#    return e.decisions[id]


#def returnForDisplay(endpointName, item,threshold=0.5):
    
    ## return data that enters the visualisation function
    
    #pass 