import os
import yaml

from toxtrust.config import endpointPath
from toxtrust.evidence import Evidence
from toxtrust.combination import Combination
from toxtrust.visualisation import plotBeliefPlausibility

class Endpoint:
    
    def __init__(self, endpointName):
        
        self.name = endpointName
        self.path = endpointPath(endpointName)
        
        self.endpoint = {
            'name': str,
            'id': None,
            'framework' : str,
            'compound': str,
            'confidentiality': str    
            }
    
        self.input = {}
        self.options = {
            'decision': {
                'maxUncertainty': 0.3,
                'minBelief':0.5
                },
            'combination' : {
                'autoRule' : True,
                'autoExplanation' : None,
                'rule': None,
                'inagakiScale': 0.5,
                'maxUncertainty': 0.3,
                'woe' : False,
                'shouldCombine': []
            }
        }
        self.evidence = {}
        self.results = {}
        self.decisions = {}
        
    def load(self):
               
        ''' loads the endpoint object from a YAML file
        '''
        # obtain the path and the default name of the raname parameters
        if not os.path.isdir (self.path):
            return False, f'Endpoint "{self.endpoint}" not found'

        # load the main class dictionary (p) from this yaml file
        
        template = os.path.join (self.path,'endpoint.yaml')
        
        if not os.path.isfile(template):
            return False, f'Template {template} not found'

        # load status from yaml
        templateDict = {}
        
        try:
            with open(template, 'r') as pfile:
                templateDict = yaml.safe_load(pfile)
        except Exception as e:
            return False, f'error:{e}'

        # validate templateDict
        
        ## checkkkk 
        keylist = ['endpoint','input', 'options', 'evidence', 'results']
        for ikey in keylist:
            if templateDict[ikey] != None:
                self.__dict__[ikey] = templateDict[ikey]
                
        return templateDict     # temporary   
        
                   
    def save (self):
        
        ''' saves the template object to a YAML file
        '''
        
        template = os.path.join (self.path,'endpoint.yaml')

        templateDict = {
            'endpoint': self.endpoint,
            'input': self.input,
            'options': self.options, 
            'evidence': self.evidence,
            'results': self.results,
            'decisions': self.decisions
        }
        
        with open(template,'w') as f:
            f.write(yaml.dump(templateDict))

    def getVal(self, key):
        
        ''' returns self.dict value for a given key
        '''
        
        if key in self.endpoint:
            return self.endpoint[key]
        else:
            return None

    def setVal(self, key, value):
        
        ''' sets self.dict value for a given key, either replacing existing 
            values or creating the key, if it doesn't exist previously
        '''
        # for existing keys, replace the contents of 'value'
        if key in self.endpoint:
            self.endpoint[key] = value
        # for new keys, create a new element with 'value' key
        else:
            self.endpoint[key] = value
            
    def endpointInput(self, userEndpoint: dict):
        
        ''' uses provided dictionary to set self.endpoint values for all requested keys
        '''
    
        try:
            # check if keys provided correctly
            for key, value in userEndpoint.items():
                if key != 'id':
                    if key in self.endpoint:
                        self.endpoint[key] = value 
            # return True, 'Evidence added correctly'
        except:
            return False, 'Evidence keys not matching the required style'   
        
        return True, 'Endpoint information successfully added'   
        
    def evidenceInput(self, id: str, userInput: dict):
        
        if id == self.name:
            return False, 'Name already taken'
        
        evidenceDict = { 
            #'name': None,
            'source': None,
            'result': None,
            'reliability': None,
            'relevance' : 'certain',    # default
            'weight': 1                 # default
            }

        try:
            for key, value in userInput.items(): 
                if key in evidenceDict:
                    evidenceDict[key] = value
            self.input[id] = userInput    
        except:
            return False, 'Evidence keys not matching the required style'    
        
        item = Evidence(userInput)
        self.evidence[id] = item.returnEvidence()
        self.results[id] = item.returnResults()
        
    def decisionInput(self, userDecision: dict):
        
        decisionDict = self.options['decision']
            
        try:
            for key, value in userDecision.items(): 
                if key in decisionDict:
                    if value != decisionDict[key] and type(value) == float:
                        decisionDict[key] = value
            self.options['decision'] = userDecision    
        except:
            return False, 'Decision input not matching the required style'   
    
    def combinationRule(self, userRule: str):
        
        if userRule not in ['auto', 'Dempster', 'Yager', 'Inagaki']:
            return False, 'Rule not indicated correctly'
        elif userRule != 'auto':
            self.options['combination']['autoRule'] = False
            self.options['combination']['rule'] = userRule   
            
    def combinationInput(self, userCombination: dict):   # userCombination = {'inagakiScale': 0.5, 'maxUncertainty': 0.3,'woe' : False}
        
        combinationDict = self.options['combination']
        
        try:
            for key, value in userCombination.items(): 
                if key in combinationDict:
                    if value != combinationDict[key]:
                        combinationDict[key] = value
            self.options['combination'] = combinationDict   

        except: 
            return False, 'Combination options not matching the required style' 
        
    def shoudCombine(self, shouldCombine: list):
        
        available = []
        
        for item in shouldCombine:
            if item in self.input.keys():
                available.append(item)
            else:
                return False, f'{item} not available in the provided evidence'
        
        self.options['combination']['shouldCombine'] = available
        
        # return True  , ''

    def runCombination(self):
        
        options = self.options['combination']
        
        combo = Combination(options)
        
        if not options['shouldCombine']:
            return False, 'No item for combination selected'
        else:
            for id in options['shouldCombine']:
                userInput = self.input[id]
                
                combo.addItem(id, Evidence(userInput))
            
            combo.executeCombination()
            self.results['combination'] = combo.returnResults()
        
    def returnResult(self, id : str, selection = None):

        if id in self.results.keys():
            result = self.results[id]
                     
            if selection == None:
                return result
            else:
                if selection in ['probabilities', 'belief', 'plausibility']:
                    return result[selection]
                else:
                    return False, f'{selection} not computed in the results'
        else:
            return False, f'{id} not found in results'
        
    #### make decision and visualisation go to utils (visualisation.py)
        
    def makeDecision(self, id: str):
        
        if id != 'combination':
            if id not in self.input.keys():
                return False, f'{id} not available in the provided evidence'
        
        uncertainty = self.results[id]['probabilities']['uncertain']
        beliefs = self.results[id]['belief']
        
        maxUncertainty = self.options['decision']['maxUncertainty']
        minBelief = self.options['decision']['minBelief']
    
        for key, value in beliefs.items():
    
            if (uncertainty >= maxUncertainty or value <= minBelief):
                decision = 'uncertain'
                
            else:
                decision = key
                break

        self.decisions[id] = decision
    
    def returnDecision(self, id: str):
        
        if id in self.decisions.keys():
            return self.decisions[id] 
        else:
            return False, f'{id} not found in decisions'
        
#    def showIntervals(self, id: str):
        
#        item = self.results[id]
#        threshold = self.options['decision']['minBelief']
        
#        plotBeliefPlausibility(item, threshold)
        
        
        