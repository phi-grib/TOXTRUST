import pandas as pd
import numpy as np
import math
import itertools
import os

class evidence:
    
    def __init__(self):
        
        self.evidence = {
            'name': None,
            'source': None,
            'result': None,
            'reliability': None,
            'relevance' : 'certain',    # not obligatory
            'weight': 1                 # not obligatory
        }
        
        self.results = {
            'probabilities': None,
            'belief': None,
            'plausibility': None        
        }
        
    def addEvidence(self, data):

        try:
            for key, value in data.items():
                if value != None:
                    if key == 'result':
                        self.evidence[key] = self.processResult(data['source'], value)
                    elif key == 'reliability':
                        self.evidence[key] = self.processReliability(value)
                    else:    
                        self.evidence[key] = value
                elif value == None:
                    pass                
        except:
            return False, "Evidence not indicated correctly."
        
        self.basicProbabilityMasses()
        self.beliefPlausibility()
        
    # def saveEvidence(self):
        
    #     yaml = load(self.endpointPath, self.endpointName)
        
    #     yaml['evidence'][self.id] = {'evidence': self.evidence, 'results': self.results}
        
    #     save(yaml, self.endpointPath, self.endpointName)
        
    # def updateEvidence(self, key, value): ### maybe not necessary
       
    #    evidence = self.evidence
       
    #    try: 
    #         self.addData(evidence.update({key:value}))
    #    except:
    #        return False, "Evidence piece not indicated correctly"

    def booleanTest(self, r):
    
        return 'boolean' if np.isin(r, [1,0]).all() == True else 'non-boolean'
    
    def processResult(self, source, result): 
        
        try:
            methods = pd.DataFrame({
                'boolean':['singleClassPositive','singleClassPositive','singleClassPositive','singleClassPositive','singleClassNegative'], 'non-boolean':['twoClassesProbability','singleClassProbability',None,None,None]
                }, index=['qsar','expert','in vitro', 'positive alert', 'negative alert'])

            evidenceType = methods.at[source.lower(),self.booleanTest(result)]

            if evidenceType == 'twoClassesProbability': # predict proba

                processed = result

            elif evidenceType == 'singleClassProbability': # expert single number

                pos = result/100 if result > 1 else result
                neg = 1 - pos
                processed = np.array([neg,pos]).T

            elif evidenceType == 'singleClassPositive': #alert or prediction - predict normal 

                pos = result
                neg = 1 - pos
                processed = np.array([neg,pos]).T   ### check how to include the change for the expert, binary one number and level of ignorance

            elif evidenceType == 'singleClassNegative': #alert or prediction - predict normal 

                neg = result
                pos = 1 - neg
                processed = np.array([neg,pos]).T
    
            return processed
        
        except:
            return False, "Processing result failed."

    def processReliability(self, reliability):
        
        try: 
            if type(reliability) == list:
                processed = {'negative': reliability[0], 'positive': reliability[1]}
            else:

                reliability = reliability / 100 if reliability > 1 else reliability
                processed = {'negative': reliability, 'positive': reliability}

            return processed
        except:
            return False, "Processing reliability failed."

    def basicProbabilityMasses(self):
        
        relevanceDict = {'certain':1,'probable':0.9,'plausible':0.75,'equivocal':0.5, 'doubted':0.25,'improbable':0.1,'impossible':0}

        evidence = self.evidence['result']
        reliability = self.evidence['reliability']
        relevance = relevanceDict[self.evidence['relevance']]
        
        bpaNegative = round(evidence[0] * reliability['negative'] * relevance,2)
        bpaPositive = round(evidence[1] * reliability['positive'] * relevance,2)
        ignorance = round(1 - (bpaPositive + bpaNegative),2)

        self.results['probabilities'] = {             # np.array([bpaNegative, ignorance, bpaPositive])
            'negative': bpaNegative,
            'uncertain': ignorance,
            'positive': bpaPositive
            }
        
    def beliefPlausibility(self):
        
        bpa = self.results['probabilities']

        beliefNegative = bpa['negative']  #  belief == plausibility because 
        beliefPositive = bpa['positive'] 
        
        self.results['belief'] = {
            'negative' : beliefNegative,
            'positive' : beliefPositive
        }
        
        plausibilityNegative = 0 if beliefNegative == 0 else beliefNegative + bpa['uncertain']
        plausibilityPositive = 0 if beliefPositive == 0 else beliefPositive + bpa['uncertain']

        self.results['plausibility'] = {
            'negative' : plausibilityNegative,
            'positive' : plausibilityPositive
        }

    ### leave for later ###

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
    
