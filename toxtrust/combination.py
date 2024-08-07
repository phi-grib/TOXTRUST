import pandas as pd
import numpy as np
import math
import itertools
import os
from IPython.display import display
class Combination:
    
    def __init__(self, ruleOptions : dict):
        
        self.evidence = {
           # 'name' : None,
            'bpm' : {},
            'weights' : {},
            'gpm': None           
        }

        self.rule = ruleOptions

        #  combination = {
        #         'autoRule' : True,
        #         'autoExplanation' : None,
        #         'rule': None,
        #         'inagakiScale': 0.5,
        #         'maxUncertainty': 0.3,
        #         'woe' : False,
        #         'weights': [],
        #         'shouldCombine': []
        #     }
        
        self.results = {
            'probabilities': None,
            'belief': None,
            'plausibility': None    
        }
    
    def addItem(self, id: str, weight: int, probabilities: dict):
        
        if not weight or not probabilities:
            return False, 'Item selected wrongly'
        else:
            # self.evidence['bpm'] = probabilities
            # self.evidence['weights'] = weight
        
            self.evidence['bpm'][id] = probabilities
            self.evidence['weights'][id] = weight
            
        return True, 'Item added correctly to combination'
        
        
        #self.groundProbabilityMasses()
        
    # def addItemManually(self, id, bpm, weight=1):
        
    #     try:
    #         self.evidence['bpm'][id] = bpm
    #         self.evidence['weights'][id] = weight 
    #     except:
    #         return False, "Evidence item not provided correctly"
        
    #     self.groundProbabilityMasses()

    # def returnItemList(self):
        
    #     return [key for key in self.evidence['bpm'].keys()]
    
    # def popItem(self, item):
        
    #     try:
    #         self.evidence['bpm'].pop(item)
    #     except:
    #         return False, "Evidence item not indicated correctly"
    
    # def updateWeights(self, id, weight):  
            
    #     if id in self.evidence['weights'].keys() and type(weight) == int:
    #         self.evidence['weights'][id] = weight
    #     else:
    #         return False, "Evidence piece not indicated correctly"
        
    def weigtOfEvidence(self):
        
        if len (self.evidence['bpm']) != 0:
            self.groundProbabilityMasses()

    def processWeigtOfEvidence(self):
        
        try:
            woeDict = {}
            
            for key, value in self.evidence['bpm'].items():
                weight = self.evidence['weights'][key]
                count = 1
                
                while count <= weight:
                    newKey = key + "_" + str(count)
                    value = value
                    
                    woeDict[newKey] = value
                    count += 1
            return True, woeDict
        except:
            return False, "Weighting evidence failed"
    
    def processGroundProbabilityMasses(self, df, iterations): 

        gpm = 0
        
        try:
            for element in iterations:
                count = 1

                for index, row in df.iterrows():
                    count = count * row[element[index]] 
                gpm += count
            return True, gpm
        except:
            return False, "Computation of ground probability mass failed"
    
    # def returnGroundProbabilityMasses(self):
        
    #     if self.evidence['gpm'] == None:
    #         self.groundProbabilityMasses() 
        
    #     return self.evidence['gpm']

    def groundProbabilityMasses(self):
        
        woe = self.rule['woe']
        
        #data = self.processWeigtOfEvidence() if woe == True else self.evidence['bpm']
        
        if woe == True:
            success, result = self.processWeigtOfEvidence()
            if not success:
                return False, result
            else:
                data = result
        else:
            data = self.evidence['bpm']
        
        try: 
            length = len(data.keys())
            df = pd.DataFrame.from_dict(data,orient='index').rename(columns={"negative": "N", "uncertain": "U", "positive":"P"})
            df.reset_index(inplace=True,drop=True)
            # iterating through the added items

            iterationsNegative = list(itertools.product('NU',repeat=length))[:-1:]
            iterationsPositive = list(itertools.product('PU',repeat=length))[:-1:]

            # computing ground probability masses

            success, gpmNegative = self.processGroundProbabilityMasses(df, iterationsNegative)
            if not success:
                return False, gpmNegative + 'for the negative result'
            
            success, gpmPositive = self.processGroundProbabilityMasses(df, iterationsPositive)
            if not success:
                return False, gpmPositive + 'for the positive result'
            
            gpmUncertain = df['U'].prod()
            gpmConflict = 1 - (gpmNegative + gpmPositive + gpmUncertain)
            
            self.evidence['gpm'] = {             
                'negative': gpmNegative,
                'uncertain': gpmUncertain,
                'positive': gpmPositive,
                'conflict': gpmConflict
                }
            
            return True, 'Ground probability masses computed successfully'
        except:
            return False, 'Processing ground probability masses failed'
    
    def dempsterRule(self):
        
        try:
            gpmNegative = self.evidence['gpm']['negative']
            gpmPositive = self.evidence['gpm']['positive']
            gpmUncertain = self.evidence['gpm']['uncertain']
            gpmConflict = self.evidence['gpm']['conflict']
            
            k = 1 - gpmConflict

            jpmNegative = round(gpmNegative/k,2)
            ignorance = round(gpmUncertain/k,2)
            jpmPositive = round(gpmPositive/k,2)
            
            combination = np.array([jpmNegative, ignorance, jpmPositive])

            while not math.isclose(combination.sum(), 1.0, abs_tol=0.01):
                ignorance += 0.01
                
            self.results['probabilities'] = {             
            'negative': jpmNegative,
            'uncertain': ignorance,
            'positive': jpmPositive
            }
            
            return True, 'Dempster combination executed successfully'
        except:
            return False, 'Dempster combination rule failed'
        
    def yagerRule(self):
        
        try:
            gpmNegative = self.evidence['gpm']['negative']
            gpmPositive = self.evidence['gpm']['positive']
            gpmUncertain = self.evidence['gpm']['uncertain']        

            print(gpmNegative)
            print(gpmPositive)

            jpmNegative = round(gpmNegative,2)
            jpmPositive = round(gpmPositive,2)
            ignorance = round(1 - (gpmNegative + gpmPositive),2)
        
            combination = np.array([jpmNegative, ignorance, jpmPositive])

            while not math.isclose(combination.sum(), 1.0, abs_tol=0.01):
                ignorance += 0.01
                
            self.results['probabilities'] = {             
            'negative': jpmNegative,
            'uncertain': ignorance,
            'positive': jpmPositive
            }
            
            
            return True, 'Yager combination executed successfully'
        except:
            return False, 'Yager combination rule failed'
        
    def inagakiRule(self):
        
        try:
            gpmNegative = self.evidence['gpm']['negative']
            gpmPositive = self.evidence['gpm']['positive']
            gpmUncertain = self.evidence['gpm']['uncertain']
            gpmConflict = self.evidence['gpm']['conflict']
        
            c = (1 / (1 - gpmUncertain - gpmConflict)) * self.rule['inagakiScale']

            jpmNegative = round(gpmNegative * (1 + c * gpmConflict),2)
            ignorance = round((1 + c * gpmConflict) * (gpmUncertain + gpmConflict ) - c * gpmConflict,2)
            jpmPositive = round(gpmPositive * (1 + c * gpmConflict),2)
            
            combination = np.array([jpmNegative, ignorance, jpmPositive])
                    
            while not math.isclose(combination.sum(), 1.0, abs_tol=0.01):
                ignorance += 0.01
                
            self.results['probabilities'] = {             
            'negative': jpmNegative,
            'uncertain': ignorance,
            'positive': jpmPositive
            }
            
            # self.beliefPlausibility()
            return True, 'Inagaki combination executed successfully'
        except:
            return False, 'Inagaki combination rule failed'
        

    # def autoRuleMaxUncertainty(self, maxUncertainty): 
        
    #     self.rule['maxUncertainty'] = maxUncertainty
    
    def autoRuleSelection(self):
        
        data = self.evidence['bpm']
        maxUncertainty = self.rule['maxUncertainty']      

        result = []

        try:
            for value in data.values():
                maxConflict = (value['negative'] + value['positive'])/2
            
                if value['negative'] > maxConflict:
                    result.append('n')
                
                if value['uncertain'] > maxUncertainty:
                    result.append('u')

                if value['positive'] > maxConflict:
                    result.append('p')
                
            if len(set(result)) == 1:
                
                autoExplanation = 'Executed Dempster\'s rule: Agreement between sources and none exceeding the uncertainty threshold.'
                
                self.rule['autoExplanation'] = autoExplanation
                self.rule['rule'] = 'Dempster'
                
            elif 'u' in set(result):
                
                autoExplanation = 'Executed Yager\'s rule: Uncertainty threshold exceeded.'
                
                self.rule['autoExplanation'] = autoExplanation
                self.rule['rule'] = 'Yager'
                
            else: 
                autoExplanation = 'Executed Inagaki\'s rule: No agreement between sources.'
                
                self.rule['autoExplanation'] = autoExplanation
                self.rule['rule'] = 'Inagaki'
                
            return True, 'Rule autoselection successfully completed'
        except:
            return False, 'Rule autoselection failed'
        
    def executeCombination(self):
        
        self.rule['autoExplanation'] = None
        
        success, message = self.groundProbabilityMasses()
        if not success:
            return False, message
        
        methods = {'Dempster': self.dempsterRule, 'Yager': self.yagerRule, 'Inagaki': self.inagakiRule}
        
        if self.rule['autoRule'] == True:
            success, message = self.autoRuleSelection()
            if not success:
                return False, message                

        if self.rule['rule'] not in ['Dempster', 'Yager', 'Inagaki']:
            return False, 'Rule not indicated correctly'
        else:
            # rule = self.rule['rule']
        
            # if rule == 'Dempster':
            #     self.dempsterRule()
            # elif rule == 'Yager':
            #     self.yagerRule()
            # elif rule == 'Inagaki':
            #     self.inagakiRule()
                
            success, message = methods[self.rule['rule']]()
            if not success:
                return False, message
            else:
                success_, message_ = self.beliefPlausibility()
                if not success_:
                    return False, message_
                else:
                    if type(self.rule['autoExplanation']) == str:
                        return True, 'Combination of evidence successfully completed. ' + self.rule['autoExplanation']
                    else:
                        return True, 'Combination of evidence successfully completed'
            
    def beliefPlausibility(self):
        
        try:
            jpm = self.results['probabilities']

            beliefNegative = jpm['negative']  #  belief == plausibility because 
            beliefPositive = jpm['positive'] 
            
            self.results['belief'] = {
                'negative' : beliefNegative,
                'positive' : beliefPositive
            }
            
            plausibilityNegative = round(0 if beliefNegative == 0 else beliefNegative + jpm['uncertain'],2)
            plausibilityPositive = round(0 if beliefPositive == 0 else beliefPositive + jpm['uncertain'],2)

            self.results['plausibility'] = {
                'negative' : plausibilityNegative,
                'positive' : plausibilityPositive
            }
            
            return True, 'Belief and Plausibility computed successfully'
        except:
            return False, 'Computing Belief and Plausibility failed'
        
    def returnResults(self):
    
        r = self.results.copy()
        
        check = ['probabilities', 'belief', 'plausibility']
        
        for key in check:
            if r[key] is None:
                return False, 'Results not processed correctly'
            else:
                r[key] = {key: value.tolist() if isinstance(value, np.float64) else value for key, value in r[key].items() }
                    
        return True, r  

    # def returnBelief(self):
            
    #     if self.results['belief'] == None:
    #         self.beliefPlausibility() 
            
    #     return self.results['belief']
    
    # def returnPlausibility(self):
            
    #     if self.results['plausibility'] == None:
    #         self.beliefPlausibility() 
            
    #     return self.results['plausibility']


        
        
    #def autoRule(self):
    
    #    self.rule['autoRule'] = True
    #    try:
    #        self.autoRuleSelection()
    #    except:
    #        return False, "Rule autoselection failed"
