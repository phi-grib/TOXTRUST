import os
from toxtrust.config import endpointRepositoryPath, updateConfig
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
    success, content = e.load()
    
    if not success:
        return False, content
    
    success, message = e.evidenceInput(userEvidence)
    if not success:
        return False, message
    
    e.save()
    return True, message

def pathEvidencePlot(endpointName, id : int):
    
    e = Endpoint(endpointName)
    success, content = e.load()
    
    if not success:
        return False, content
    
    if id in e.results.keys():
        path_plot = os.path.join(e.path, id + '.png')
        return True, path_plot
    else:
        return False, f'Path for {id} cannot be created'
    
    
def pathCombinationPlot(endpointName):
    
    e = Endpoint(endpointName)
    success, content = e.load()
    
    if not success:
        return False, content
    
    path_plot = os.path.join(e.path, 'combination.png')
    if os.path.isfile(path_plot):
        return True, path_plot
    else:
        return False, f'Path for combination plot cannot be created'
     

def removeEvidence(endpointName, id : str):
    
    """"
    Removes the selected evidence piece by accessing it's name from the yaml file.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.deleteEvidence(id)
    if not success:
        return False, message
    
    e.save()
    return True, message   

def removeCombination(endpointName):

    """"
    Removes combination results from the yaml file.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.deleteCombination()
    if not success:
        return False, message
    
    e.save()
    return True, message   

def returnEvidenceInput(endpointName):
    
    """ Returns added evidence to the yaml file. """
    
    e = Endpoint(endpointName)
    e.load()
    
    return True, e.evidenceRaw

def returnEndpointInfo(endpointName):
    
    """ Returns added evidence to the yaml file. """
    
    e = Endpoint(endpointName)
    e.load()
    
    return True, e.endpoint


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

def selectRule(endpointName, rule = 'auto', factor = 0.5):
    
    """
    Function to define the combination rule.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.combinationRule(rule, factor)
    if not success:
        return False, message
    
    e.save()
    return True, message

# def callCombinationUncertainty(endpointName, combinationUncertainty: float): #, default=True):    # combinationDict = {'inagakiScale': 0.5, 'maxUncertainty': 0.3} 
#                                                                   # pass default settings to this function (dict above)
    
#     """
#     Function to add combination settings.
#     """
    
#     e = Endpoint(endpointName)
#     e.load()
    
#     success, message = e.combinationUncertainty(combinationUncertainty)
#     if not success:
#         return False, message
    
#     e.save()
#     return True, message

def shouldCombineInput(endpointName, list_to_combine: list): ### THIS NEEDS TO GO BEFORE the next function
    
    """
    Select evidence pieces by IDs to be combiened later.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    if len(list_to_combine) == 0:
        return False, 'Evidence pieces for combination not selected'
    
    success, message = e.shoudCombine(list_to_combine)
    if not success:
        return False, message
    
    if e.options['combination']['woe']:
        weights = []
        
        for i in list_to_combine:
            weights.append(e.evidence[i]['weight'])

        e.options['combination']['weights'] = weights
    e.save()
    return True, message

def shouldWoeInput(endpointName, WoE:bool): ## 

    """
    Function getting user answer whether Weight of Evidence should be added to evaluating the evidence.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    # weights = []
    
    # s = e.options['combination']['shouldCombine']
    
    # if len(s) == 0:
    #     return False, 'Evidence pieces for combination not selected'
    
    # for i in s:
    #     weights.append(e.evidence[i]['weight'])
    
    
    success, message = e.shouldWoE(WoE)
    if not success:
        return False, message
    
    e.save()
    
    return True, message

def returnComputedResult(endpointName, id : str, selection = None): #id
    
    """
    Returns a single evidence object using info stored in the YAML using evidence name.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.returnResult(id , selection)
    if not success:
        return False, message
    
    return True, message
    
def runCombine(endpointName): #pass should combine
    
    """
    Main function to combine evidence, following the stored settings.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, result = e.runCombination()
    if not success:
        return False, result
    
    e.save()
    return True, result
    
# def returnCombination(endpointName, selection = None): 
    
#     """
#     Return evidence after combination.
#     """
 
#     e = Endpoint(endpointName)
#     e.load()
    
#     success, result = e.returnCombinationResult(selection) 
#     if not success:
#         return False, result
    
#     return True, result

def runDecisionFunction(endpointName, selection: str): 
    
    """
    Makes a decision for the selected evidence piece or the combination. 
    """

    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.makeDecision(selection)
    if not success:
        return False, message
    
    e.save()
    return True, message
    
def returnDecisionResult(endpointName, selection: str): 
    
    """
    Makes a decision for the selected evidence piece or the combination. 
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, result = e.returnDecision(selection)
    if not success:
        return False, result
    
    return True, result


def plotIntervals(endpointName, id: str): 
    
    """
    Generates an interval plot and stores in the endpoint folder.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.probabilityIntervals(id)
    return success, message

def plotCombination(endpointName): 
    
    """
    Generates a probability plot and stores in the endpoint folder.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, message = e.combinationIntervals()
    return success, message

def updateConfiguration():
    
    """
    Updates configuration settings. 
    """

    success, message = updateConfig()
    return success, message

def returnConfiguration():
    
    """
    Returns the configuration path. 
    """
    
    try:  
        path = endpointRepositoryPath()
        return True, path
    except:
        return False, "Returning path failed"


#def returnForDisplay(endpointName, item,threshold=0.5):
    
    ## return data that enters the visualisation function
    
    #pass 
    
def returnDataErrorPlot(endpointName, id:str): 
    
    """
    Generates an interval plot and stores in the endpoint folder.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, result = e.dataErrorPlot(id)
    return success, result
    

def returnDataCombinationPlot(endpointName): 
    
    """
    Generates an interval plot and stores in the endpoint folder.
    """
    
    e = Endpoint(endpointName)
    e.load()
    
    success, result = e.dataCombinationPlot()
    return success, result