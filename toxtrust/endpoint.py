import os
import yaml
import numpy as np

from toxtrust.config import endpointPath
from toxtrust.evidence import Evidence
from toxtrust.combination import Combination
from toxtrust.visualisation import beliefPlausibility, visualiseCombination

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
        self.evidenceRaw = {}
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
        keylist = ['endpoint', 'options', 'evidence', 'evidenceRaw', 'results', 'decisions']
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
            'evidenceRaw': self.evidenceRaw,
            'results': self.results,
            'decisions': self.decisions
        }
        
        with open(template,'w') as f:
            f.write(yaml.dump(templateDict, sort_keys=False))

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
            self.evidenceRaw[identifier] = userInput
            
            success_, results = i.returnResults()
            if not success_:
                return False, 'Accessing results failed'
            else: 
                self.results[identifier] = results

                # path = self.path
                # threshold = self.options['decision']['minBelief']
                
                success, decision_message = self.makeDecision(identifier)
                if not success:
                    return False, decision_message
                
                # success, plot_message = self.probabilityIntervals(identifier)
                
                # if not success:
                #     return False, plot_message
  
        return True, message  
    
    def deleteEvidence(self, id: str):

        #removePath = os.path.join(self.path, id + '.png')
        
        if id in self.evidence.keys():
            self.evidence.pop(id)
            self.evidenceRaw.pop(id)
            self.results.pop(id)
            self.decisions.pop(id)

            # if os.path.exists(removePath):

            #     os.remove(removePath)
            # else:
            #     return False, 'Image not found'
            
            return True, 'Evidence piece removed'
        else:
            return False, 'Accessing evidence failed'      
         
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
        self.options['combination']['maxUncertainty'] = userDecision['maxUncertainty']
            
        return True, 'Decision input successfully added'  
    
    def combinationRule(self, userRule: str, factor: float):
        
        if userRule not in ['auto', 'Dempster', 'Yager', 'Inagaki']:
            return False, f'Rule "{userRule}" not available'
        elif userRule != 'auto':
            self.options['combination']['autoRule'] = False
            self.options['combination']['rule'] = userRule 
            
            message = 'Rule selection successfully completed'  
            
            if userRule == 'Inagaki':

                if not 0 <= factor <= 1:
                    return False, 'Inagaki factor is outside the range [0,1]'
                else:
                    self.options['combination']['inagakiScale'] = factor
                    
                message += ', Inagaki factor considered'  
        else:
            self.options['combination']['autoRule'] = True

            
            message = 'Auto-rule selected'
            return True, message
            
        return True, message
            
    # def combinationUncertainty(self, userUncertainty):
        
    #     if type(userUncertainty) == float:
    #         self.options['combination']['maxUncertainty'] = userUncertainty
    #     elif type(userUncertainty) == int:  
    #         userUncertainty = float(userUncertainty)
    #         self.options['combination']['maxUncertainty'] = userUncertainty
    #     else:
    #         return False, 'Uncertainty input not matching the required style' 

    #     return True, 'Uncertainty settings successfully updated' 
    
    def shouldWoE(self, WoE: bool):
        
        
        if not type(WoE) == bool:
            return False, 'Wrongly defined input for Weight of Evidence'

        else:
            self.options['combination']['woe'] = WoE
            #self.options['combination']['weights'] = weights            
            
            if WoE == True:
                return True, 'Weight of Evidence added to settings'
            else:
                self.options['combination']['weights'] = []
                
                return True, 'Weight of Evidence excluded from settings'

    def shoudCombine(self, shouldCombine: list):
        
        available = []
        weights = []
        
        if len(shouldCombine) < 2:
            return False, 'Combination not possible, increase the number of evidence pieces'   
        else:
            for item in shouldCombine:
                if item in self.results.keys():
                    available.append(item)
                    weights.append(self.evidence[item]['weight'])
                else:
                    return False, f'{item} not available in the provided evidence'
            
        self.options['combination']['shouldCombine'] = available
        self.options['combination']['weights'] = weights
        
        return True, 'Evidence pieces for combination saved correctly'

    def returnResult(self, id : str, selection):
        
        if id in self.results.keys():
            result = self.results[id]
                     
            if selection == None:
                return True, result
            else:
                if selection in ['probabilities', 'belief', 'plausibility']:
                    return True, result[selection]
                else:
                    return False, f'{selection} not available'
        elif id in self.evidence.keys() or id == self.name:
            return False, f'{id} not yet computed'
        else:
            return False, 'Error returning result'
        
    def runCombination(self):
        
        options = self.options['combination']
        
        c = Combination(options)
        identifier = self.name
        if not options['shouldCombine']:
            return False, 'Evidence pieces for combination not selected'
        else:
            for num, i in enumerate(options['shouldCombine']):
                
                w =  options['weights'][num]
                bpm = self.returnResult(i, selection='probabilities')[1]

                
                success, message = c.addItem(i, w, bpm)
                if not success:
                    return False, message
                    
            success_combination, message_combination = c.executeCombination()       
            if not success_combination:
                return False, message_combination
                
            success_results, result = c.returnResults()
            
            if not success_results:
                return False, result
            
            else:
                self.results[identifier] = result   ## 
                
                success, decision_message = self.makeDecision(identifier)
                if not success:
                    return False, decision_message
                
                
                # success, plot_message = self.combinationIntervals()
                
                # if not success:
                #     return False, plot_message

            return True, message_combination
    
    def deleteCombination(self):

        #removePath = os.path.join(self.path, 'combination.png')
        
        if self.name in self.results.keys():
            self.results.pop(self.name)
            self.decisions.pop(self.name)

            # if os.path.exists(removePath):
            #     os.remove(removePath)
            # else:
            #     return False, 'Image not found'
            
            return True, 'Combination result removed'
        else:
            return False, 'Accessing combination result failed'       
        
            
        

    # def returnCombinationResult(self, selection):
        
    #     if self.name in self.results.keys():
    #         result = self.results[self.name]
    #     else:
    #         return False, f'Combination result for endpoint {self.name} not found in results'  
                     
    #     if selection == None:
    #         return True, result
    #     else:
    #         if selection in ['probabilities', 'belief', 'plausibility']:
    #             return True, result[selection]
    #         else:
    #             return False, f'{selection} not available'  

    def makeDecision(self, selection: str):

        if selection not in self.results.keys():
            return False, f'No results computed for "{selection}", decision-features not available'
    
        uncertainty = self.results[selection]['probabilities']['uncertain']
        beliefs = self.results[selection]['belief']
        
        maxUncertainty = self.options['decision']['maxUncertainty']
        minBelief = self.options['decision']['minBelief']
    
        for key, value in beliefs.items():
    
            if (uncertainty >= maxUncertainty or value <= minBelief):
                decision = 'uncertain'
                
            else:
                decision = key
                break

        self.decisions[selection] = decision
        
        return True, f'Decision making for {selection} successfully completed'
    
    def returnDecision(self, selection: str):
        
        if selection in self.decisions.keys():
            decision = self.decisions[selection]
            return True, decision
        else:
            return False, f'Check if results were computed for "{selection}" and make a decision first.'
        
        
    def dataErrorPlot(self, id: str):
        
        if id in self.results.keys():
            result = self.results[id]

        elif id in self.evidence.keys() or id == self.name:
            return False, f'{id} not yet computed'
        else:
            return False, 'Error returning result'

        threshold = self.options['decision']['minBelief']
        
        data_bounds = {'Negative': round(result['belief']['negative'] + (result['plausibility']['negative'] - result['belief']['negative'])/2,2),'Positive': round(result['belief']['positive'] + (result['plausibility']['positive'] - result['belief']['positive'])/2,2)}
        error = round(result['probabilities']['uncertain']/2,2) # assuming equal ledatael of ignorance for each prediction from a constant source
        
        labels, data = [], []

        for key, value in data_bounds.items():

            if value != 0:

                labels.append(key)
                data.append(value)
                
        return True, [labels, data, error, threshold]
 
    def probabilityIntervals(self, id: str):
        
        if id in self.results.keys():
            result = self.results[id]

        elif id in self.evidence.keys() or id == self.name:
            return False, f'{id} not yet computed'
        else:
            return False, 'Error returning result'
        
        path = self.path
        threshold = self.options['decision']['minBelief']
        
        success, message = beliefPlausibility(id, result, threshold, path)
        
        return success, message
 
    def dataCombinationPlot(self):
        
        if self.name in self.results.keys():
            names = self.options['combination']['shouldCombine'].copy()

            if len(names) > 1:
                names.append(self.name)
                data = []
                for n in names:
                    values = self.results[n]['probabilities'].values()
                    data.append(list(values))
                
                data = np.array(data).tolist()
                #labels = ['DST' if item == self.name else item for item in names]
                #path = self.path
                
            return True, [data, names]
        else:
            return False, 'Data access failed'
 
    def combinationIntervals(self):
        
        if self.name in self.results.keys():
            names = self.options['combination']['shouldCombine'].copy()

            if len(names) > 1:
                names.append(self.name)
                data = []
                
                for n in names:
                    values = self.results[n]['probabilities'].values()
                    data.append(list(values))
                
                data = np.array(data)
                labels = ['combination' if item == self.name else item for item in names]
                path = self.path
                
                success, message = visualiseCombination(labels, data, path)
        
                return success, message
            
        else:
            return False, 'Results to display not available'
        
        