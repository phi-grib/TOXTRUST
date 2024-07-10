from toxtrust.endpoint import Endpoint

def callEndpointInput(endpointName, userEndpoint: dict):
    
    """
    This function can be used to request and collect important endpoint-relevant information from the user.

    """
    
    # userEndpoint = {
    #         'description': str,
    #         'framework' : str,
    #         'compound': str,
    #         'confidentiality': str        
    # }
    
    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.endpointInput(userEndpoint)
    if not success:
        return False, message
    
    e.save()
    return True, message

def returnEndpointContent(endpointName):
    
    """ 
    Returns everything that is stored within the new created endpoint.
    
    """

    e = Endpoint(endpointName) ## check if endpoint available not done, endpoint names predefined in the interface
    success, content = e.load()
    
    if not success:
        return False, content
    
    return success, content

def callEvidenceInput(endpointName, userEvidence : dict):
    
    """"
    Adds user provided evidence to the yaml file.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.evidenceInput(userEvidence)
    if not success:
        return False, message
    
    e.save()
    return True, message

def callDecisionInput(endpointName, userDecision : dict):   #### ask whether the user wants to keep defaults or not
    
    """
    Stores important information related with the decision making process.
    
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.decisionInput(userDecision)
    if not success:
        return False, message
    
    e.save()
    return True, message

def selectRule(endpointName, rule = 'auto'):
    
    """
    Function to define the combination rule.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.combinationRule(rule)
    if not success:
        return False, message
    
    e.save()
    return True, message

def callCombinationInput(endpointName, combinationDict: dict): #, default=True):    # combinationDict = {'inagakiScale': 0.5, 'maxUncertainty': 0.3} 
                                                                  # pass default settings to this function (dict above)
    
    """
    Function to add combination settings.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.combinationInput(combinationDict)
    if not success:
        return False, message
    
    e.save()
    return True, message

def shouldWoeInput(endpointName, WoE=False): 

    """
    Function getting user answer whether Weight of Evidence should be added to evaluating the evidence.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.shouldWoE(WoE)
    if not success:
        return False, message
    
    e.save()
    
    return True, message


def shouldCombineInput(endpointName, shouldCombine: list):
    
    """
    Select evidence pieces by IDs to be combiened later.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.shoudCombine(shouldCombine)
    if not success:
        return False, message
    
    e.save()
    return True, message

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
    
def returnDecision(endpointName, id: str):
    
    e = Endpoint(endpointName)
    
    e.load()
    
    return e.decisions[id]


#def returnForDisplay(endpointName, item,threshold=0.5):
    
    ## return data that enters the visualisation function
    
    #pass 