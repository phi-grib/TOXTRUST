import pandas as pd
import numpy as np
import math
import itertools
import os

class decisionMaker:
    
    def __init__(self):

        self.results = {
            'probabilities' : None,
            'beliefs' : None,
        }
        
        self.decision = {
            'maxUncertainty': 0.3,
            'minBelief':0.5,
            'decision' : None
        } 
        
        
    def addItem(self, item):
        
        try:
            probabilities = item.results['probabilities']
            belief = item.results['belief']
            
            self.results['probabilities'] = probabilities
            self.results['beliefs'] = belief
            
        except:
            return False, "Required item not found"
        
    def userThresholds(self, uncertainty = 0.3, decision = 0.5):
        
        self.decision['maxUncertainty'] = uncertainty
        self.decision['minBelief'] = decision
    
    def makeDecision(self):

        uncertainty = self.results['probabilities']['uncertain']
        beliefs = self.results['beliefs']
        
        maxUncertainty = self.decision['maxUncertainty']
        minBelief = self.decision['minBelief']
    
        for key, value in beliefs.items():

            if (uncertainty >= maxUncertainty or value <= minBelief):
                decision = 'uncertain'
                
            else:
                decision = key
                break

        self.decision['decision'] = decision
        
    def returnDecision(self):
                
        if self.decision['decision'] == None:
            self.makeDecision() 
            
        return self.decision['decision']