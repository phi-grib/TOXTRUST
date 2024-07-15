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
            'description': str,
            'id': None,
            'framework' : str,
            'compound': str,
            'confidentiality': str    
            }
    
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
                'weights': [],
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
        keylist = ['endpoint', 'options', 'evidence', 'results']
        for ikey in keylist:
            if templateDict[ikey] != None:
                self.__dict__[ikey] = templateDict[ikey]
                
        return True, templateDict     # temporary   
              
    def save (self):
        
        ''' saves the template object to a YAML file
        '''
        
        template = os.path.join (self.path,'endpoint.yaml')

        templateDict = {
            'endpoint': self.endpoint,
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

        i = {}

        # check if keys provided correctly
        for key, value in userEndpoint.items():
            if key != 'id':
                if key in self.endpoint:
                    i[key] = value 
                else:
                    return False, 'Evidence keys not matching the required style'
        # return True, 'Evidence added correctly'
        
        self.endpoint.update(i)
        
        return True, 'Endpoint information successfully added'   
        
    def evidenceInput(self, userInput: dict):

        i = Evidence()
        
        success, message = i.addEvidence(userInput)
        if not success:
            return False, message
    
        success, evidence = i.returnEvidence()
        
        if not success:
            return False, 'Accessing evidence failed'     
        else: 
            
            identifier = evidence['name'] ## stored in the yaml with the added "name" as key
            self.evidence[identifier] = evidence
            
            success_, results = i.returnResults()
            
            if not success_:
                return False, 'Accessing results failed'
            else: 
                self.results[identifier] = results
    
        return True, message  
         
    def decisionInput(self, userDecision: dict):
        
        decisionDict = self.options['decision']

        for key, value in userDecision.items(): 
            if key in decisionDict:
                if type(value) == float:
                    decisionDict[key] = value
                elif type(value) == int:  
                    value = float(value)
                    decisionDict[key] = value
                else:
                    return False, 'Decision input not matching the required style' 
        self.options['decision'] = userDecision    
        
        return True, 'Decision input successfully added'  
    
    def combinationRule(self, userRule: str, factor: str):
        
        if userRule not in ['auto', 'Dempster', 'Yager', 'Inagaki']:
            return False, f'Rule "{userRule}" not available'
        elif userRule != 'auto':
            self.options['combination']['autoRule'] = False
            self.options['combination']['rule'] = userRule
            
            message = 'Rule selection successfully completed'   
            
            if userRule == 'Inagaki':
                
                scaleDict = {'fullDecision': 1, 'partialDecision': 0.75, 'balance':0.5, 'partialUncertainty':0.25, 'fullUncertainty': 0}
                
                if factor not in scaleDict.keys():
                    return False, 'Inagaki factor incorrect'
                else:
                    self.options['combination']['inagakiScale'] = scaleDict[factor]
                    
                message += ', Inagaki factor considered'  
        else:
            message = 'Auto-rule selected'
            return True, message
            
        return True, message
            
    def combinationUncertainty(self, userUncertainty):
        
        if type(userUncertainty) == float:
            self.options['combination']['maxUncertainty'] = userUncertainty
        elif type(userUncertainty) == int:  
            userUncertainty = float(userUncertainty)
            self.options['combination']['maxUncertainty'] = userUncertainty
        else:
            return False, 'Uncertainty input not matching the required style' 

        return True, 'Uncertainty settings successfully updated' 
    
    def shouldWoE(self, WoE: bool, weights: list):
        
        if not type(WoE) == bool:
            return False, 'Wrongly defined input for Weight of Evidence'
        elif WoE == True:
            self.options['combination']['woe'] = True
            self.options['combination']['weights'] = weights
            return True, 'Weight of Evidence added to settings'
        else:
            return True, 'Weight of Evidence excluded from settings'

    def shoudCombine(self, shouldCombine: list):
        
        available = []
        
        if len(shouldCombine) < 2:
            return False, 'Combination not possible, increase the number of evidence pieces'   
        else:
            for item in shouldCombine:
                if item in self.results.keys():
                    available.append(item)
                else:
                    return False, f'{item} not available in the provided evidence'
            
        self.options['combination']['shouldCombine'] = available
        
        return True, 'Evidence pieces for combination saved correctly'

    def returnResult(self, id : str, selection: str):
        
        if id in self.results.keys():
            result = self.results[id]
                     
            if selection == None:
                return True, result
            else:
                if selection in ['probabilities', 'belief', 'plausibility']:
                    return True, result[selection]
                else:
                    return False, f'{selection} not available'
        else:
            return False, f'{id} not found in results'
        
    def runCombination(self):
        
        options = self.options['combination']
        
        c = Combination(options)
        
        if not options['shouldCombine']:
            return False, 'Evidence pieces for combination not selected'
        else:
            for num, i in enumerate(options['shouldCombine']): 
                w =  options['weights'][num]
                bpm = self.returnResult(i, selection='probabilities')[1]
                
                success, message = c.addItem(i, w, bpm)
                if not success:
                    return False, message
                    
            success_, message_ = c.executeCombination()       
            if not success_:
                return False, message_
                
            success__, result = c.returnResults()
            if not success__:
                return False, result

            self.results[self.name] = result        
            return True, message_

    def returnCombinationResult(self, selection):
        
        if self.name in self.results.keys():
            result = self.results[self.name]
        else:
            return False, f'Combination result for endpoint {self.name} not found in results'  
                     
        if selection == None:
            return True, result
        else:
            if selection in ['probabilities', 'belief', 'plausibility']:
                return True, result[selection]
            else:
                return False, f'{selection} not available'
              
#     #### make decision and visualisation go to utils (visualisation.py)
        
#     def makeDecision(self, id: str):
        
#         if id != 'combination':
#             if id not in self.input.keys():
#                 return False, f'{id} not available in the provided evidence'
        
#         uncertainty = self.results[id]['probabilities']['uncertain']
#         beliefs = self.results[id]['belief']
        
#         maxUncertainty = self.options['decision']['maxUncertainty']
#         minBelief = self.options['decision']['minBelief']
    
#         for key, value in beliefs.items():
    
#             if (uncertainty >= maxUncertainty or value <= minBelief):
#                 decision = 'uncertain'
                
#             else:
#                 decision = key
#                 break

#         self.decisions[id] = decision
    
#     def returnDecision(self, id: str):
        
#         if id in self.decisions.keys():
#             return self.decisions[id] 
#         else:
#             return False, f'{id} not found in decisions'
        
# #    def showIntervals(self, id: str):
        
# #        item = self.results[id]
# #        threshold = self.options['decision']['minBelief']
        
# #        plotBeliefPlausibility(item, threshold)
        
        
        