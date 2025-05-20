import pandas as pd
import numpy as np

class Evidence:
    
    def __init__(self): 
        
        self.evidence = {
            'name': None,   #str
            'source': None, #str ['qsar','expert','in vitro', 'positive alert', 'negative alert']
            'result': None,
            'reliability': None,
            'relevance' : 'certain',    # not obligatory #str
            'weight': 1                 # not obligatory #int
        }
        
        self.results = {
            'probabilities': None,
            'belief': None,
            'plausibility': None  
        }

    def addEvidence(self, data):
        
        methods = {
            'name': self.check_name,
            'source': self.check_source,
            'result': self.process_result,
            'reliability': self.process_reliability,
            'relevance': self.check_relevance,
            'weight': self.check_weight
        }
        
        output = {}
        r = data['result']['outcome']
        for key, value in data.items():
            if key in methods:

                if key in ['result','reliability']:
                    
                    inputs = list(value.values())
                    
                    success, result = methods[key](r, inputs[-2],inputs[-1])
                    
                    if not success:
                        return False, f'Processing key "{key}" resulted in the following error: {result}' # prints error message from these two functions
                else:
                    success, result = methods[key](value)
                    if not success:
                        return False, f'Processing input for "{key}" indicated as "{value}" failed'
                
                output[key] = result
            
        if len(output) == len(self.evidence):
            self.evidence = output
        else:
            return False, 'Evidence added wrongy'
        
        success, message = self.basicProbabilityMasses()
        if not success:
            return False, message
        
        success, message = self.beliefPlausibility()
        if not success:
            return False, message
            
        return True, 'Evidence added and processed correctly'    
        
    def returnEvidence(self):     
           
        e = self.evidence.copy()
        
        check = ['result', 'reliability']
        
        for key in check:
            if e[key] is None:
                return False, 'Evidence not processed correctly'
            else:
                if isinstance(e[key], np.ndarray):
                    e[key] = e[key].tolist()
    
        return True, e
                
    def returnResults(self):
        
        r = self.results.copy()
        
        check = ['probabilities', 'belief', 'plausibility']
        
        for key in check:
            if r[key] is None:
                return False, 'Results not processed correctly'
            else:
                r[key] = {key: value.tolist() if isinstance(value, np.float64) else value for key, value in r[key].items() }
                    
        return True, r

    def check_name(self, value):
        return isinstance(value, str), value
    
    def check_weight(self, value):
        if value != None:
            if value <= 5:
                return isinstance(value, int), value
            else: 
                return False, value
        else:
            return True, 1

    def check_source(self, value):
        return value in ['in silico','in vitro','expert', 'alert','read-across'], value
    
    def check_relevance(self, value):
        if value != None:
            return value in ['certain','probable','plausible','equivocal','doubted','improbable','impossible'], value
        else:
            return True, 'certain'

    def process_result(self, result:list, proba = False, num = None): 
        
        outcomes = {
            'negative' : np.array([1.,0.]),
            'positive' : np.array([0.,1.]), 
            'both' : np.array([1.,1.])
        }
        
        if not result:
            return False, 'No result indicated'
        elif len(result) == 1:
            r = outcomes[result[0]]
        elif len(result) == 2:
            r = outcomes['both']
            proba = True  ## with this the user is forced to add probability to the results !! if both classes are used
        
        if proba == True and len(result) == len(num):
            if num != None and type(num) == list and sum(num) <= 1 and len(result) == len(num):
                r *= np.array(num)
            else:
                return False, 'Probability not matching results'
        return True, r

    def process_reliability(self, result:list, metric:list, reliability:list): # rel:dict
        
        r = {'negative': 0, 'positive': 0}
        
        if not metric or not reliability:
            return False, 'Reliability not indicated correctly'
        elif not (len(metric) == len(reliability) == len(result)):
            return False, 'Lenght of indicators not matching'
        else: 
            for i, value in enumerate(result):
                r[value] = reliability[i]

        return True, r

    def basicProbabilityMasses(self):
        
        relevanceDict = {'certain':1,'probable':0.9,'plausible':0.75,'equivocal':0.5, 'doubted':0.25,'improbable':0.1,'impossible':0}

        evidence = self.evidence['result']
        reliability = self.evidence['reliability']
        relevance = relevanceDict[self.evidence['relevance']]
        
        try:
        
            bpaNegative = round(evidence[0] * reliability['negative'] * relevance,2)
            bpaPositive = round(evidence[1] * reliability['positive'] * relevance,2)
            ignorance = round(1 - (bpaPositive + bpaNegative),2)

            self.results['probabilities'] = {             # np.array([bpaNegative, ignorance, bpaPositive])
                'negative': bpaNegative,
                'uncertain': ignorance,
                'positive': bpaPositive
                }
            
            return True, 'Basic probability masses computed correctly'
        except:
            return False, 'Computing basic probability masses failed'
        
    def beliefPlausibility(self):
        
        bpa = self.results['probabilities']

        beliefNegative = bpa['negative']  #  belief == plausibility because 
        beliefPositive = bpa['positive'] 
        
        try:
            self.results['belief'] = {
                'negative' : beliefNegative,
                'positive' : beliefPositive
            }
            
            plausibilityNegative = round(0 if beliefNegative == 0 else beliefNegative + bpa['uncertain'],2)
            plausibilityPositive = round(0 if beliefPositive == 0 else beliefPositive + bpa['uncertain'],2)

            self.results['plausibility'] = {
                'negative' : plausibilityNegative,
                'positive' : plausibilityPositive
            }

            return True, 'Belief and plausibility computed correctly'
        except:
            return False, 'Computing Belief and plausibility failed'

    def returnBasicProbabilityMasses(self):
        
        if self.results['probabilities'] == None:
            self.basicProbabilityMasses() 
            
        return self.results['probabilities']
    
    def returnBelief(self):
            
        if self.results['belief'] == None:
            self.beliefPlausibility() 
            
        return self.results['belief']
    
    def returnPlausibility(self):
            
        if self.results['plausibility'] == None:
            self.beliefPlausibility() 
            
        return self.results['plausibility']
    