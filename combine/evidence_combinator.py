import pandas as pd
import numpy as np
import math
import itertools

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import display

import matplotlib.pyplot as plt
import os

class SingleEvidence:
    
    def __init__(self, identifier, source, result, reliability, relevance='certain', weight=1):
        
        """ Initiation of Single_Evidence class collecting the most important infomation associated with evidence sources and the results they provide. """
        
        self.identifier = identifier # unique model id
        self.source = source # 'expert','qsar','in vitro', 'positive alert', 'negative alert' for alerts, we need to distinct pos y neg
        self.relevance = relevance.lower() # key from dict {'certain':1,'plausible':0.9,'probable':0.75,'equivocal':0.5}
        self.weight = weight # default 1, if other specify using integers
        self.reliability, self.bpa, self.belief_plausibility = self.evidence(source, result, reliability, relevance)
        # reliability = dictionary or list of two values (starting with negative), percent (0 to 100) or point percent (0 to 1)
        
    def check_if_binary(self, r):

        return 'True_Binary' if np.isin(r, [1,0]).all() == True else 'False_Binary'
    
    def evidence(self, source, result, reliability, relevance): 

        print(f'INFO - Processed evidence identified as {self.identifier} of type {source.lower()}.')

        methods = pd.DataFrame({'True_Binary':['qualitative_one_class_p','qualitative_one_class_p','qualitative_one_class_p','qualitative_one_class_p','qualitative_one_class_n'], 'False_Binary':['quantitative_two_class','quantitative_one_class',None,None,None]}, index=['qsar','expert','in vitro', 'positive alert', 'negative alert'])
        # each source has a typical associated method  

        evidence_type = methods.at[source.lower(),self.check_if_binary(result)]

        if evidence_type == 'quantitative_two_class': #prediction - predict proba

            data = result

        elif evidence_type == 'quantitative_one_class': #expert giving a single prediction

            pos = result/100 if result > 1 else result
            neg = 1 - pos

            data = np.array([neg,pos]).T

        elif evidence_type == 'qualitative_one_class_p': #alert or prediction - predict normal 

            pos = result
            neg = 1 - pos

            data = np.array([neg,pos]).T   ### check how to include the change for the expert, binary one number and level of ignorance

        elif evidence_type == 'qualitative_one_class_n': #alert or prediction - predict normal 

            neg = result
            pos = 1 - neg

            data = np.array([neg,pos]).T

        if type(reliability) == dict:

            rel = {'reliability_negative': list(reliability.values())[0], 'reliability_positive': list(reliability.values())[1]}

        elif type(reliability) == list:

            rel =  {'reliability_negative':reliability[0],'reliability_positive':reliability[1]}

        else:

            reliability = reliability / 100 if reliability > 1 else reliability

            rel = {'reliability_negative':reliability, 'reliability_positive':reliability}

        ############## compute bpa's ############## 

        relevance_dict = {'certain':1,'probable':0.9,'plausible':0.75,'equivocal':0.5, 'doubted':0.25,'improbable':0.1,'impossible':0}

        bpa_pos = round(data[1] * rel['reliability_positive'] * relevance_dict[relevance],2)
        bpa_neg = round(data[0] * rel['reliability_negative'] * relevance_dict[relevance],2)
        ignorance = round(1 - (bpa_pos + bpa_neg),2)

        bpa = np.array([bpa_neg, ignorance, bpa_pos])

        ############## compute belief and plausibility ##############

        bel_pos = bpa_pos # only the outcome of intest aka full belief
        bel_neg = bpa_neg

        pl_pos = 0 if bel_pos == 0 else bel_pos + ignorance
        pl_neg = 0 if bel_neg == 0 else bel_neg + ignorance
        
        belief_plausibility = np.array([bel_neg, pl_neg, bel_pos, pl_pos])

        return rel, bpa,  belief_plausibility
    
    def ShowComponents(self, selection=None): # selection includes either of ['bpa', 'bp'], can be left empty  
        
        """" By selecting 'bpa', you will be able to display the basic probabilty assigment for the toxicological evidence piece. By selecting 'bp', you will view belief and probability. By just calling the function, you will see both."""
        
        
        if selection == 'bpa':
            
            print('INFO - Showing  basic probability masses computed for provided evidence ...')
            display(pd.DataFrame({self.identifier:self.bpa}, index=['Negative','Uncertain','Positive']).T.round(2))
            
        elif selection == 'bp':
            
            print('INFO - Showing the Belief and Plausibility for outcomes associated with provided evidence...')
            display(pd.DataFrame({self.identifier:self.belief_plausibility}, index = ['Belief (Negative)','Plausibility (Negative)','Belief (Positive)','Plausibility (Positive)']).T.round(2))

        else:
            print('INFO - Showing  basic probability masses computed for provided evidence ...')
            display(pd.DataFrame({self.identifier:self.bpa}, index=['Negative','Uncertain','Positive']).T.round(2))
            
            print('INFO - Showing the Belief and Plausibility for outcomes associated with provided evidence...')
            display(pd.DataFrame({self.identifier:self.belief_plausibility}, index = ['Belief (Negative)','Plausibility (Negative)','Belief (Positive)','Plausibility (Positive)']).T.round(2))

    
    def VisualiseSingleEvidence(self, visualise_threshold = 0.5, export_path=None):

        v = {'Negative': self.belief_plausibility[0] + (self.belief_plausibility[1] - self.belief_plausibility[0])/2 ,'Positive': self.belief_plausibility[2] + (self.belief_plausibility[3] - self.belief_plausibility[2])/2}

        y_error = self.bpa[1] /2 # assuming equal level of ignorance for each prediction from a constant source
        plt.figure(figsize=(3.5,2.75))

        x, y = [], []

        for key, value in v.items():

            if value != 0:

                x.append(key)
                y.append(value)

        plt.errorbar(x, y, yerr = y_error,linestyle="", capsize=6,elinewidth=2,markeredgewidth=2, color='black')#165379


        #plt.xlabel('Outcome', fontsize=15, labelpad=17)
        plt.ylabel('Probability', fontsize=13, labelpad=10)

        plt.xticks(fontsize=13)
        plt.yticks(np.arange(0, 1.05, step=0.1), fontsize=9)
        plt.ylim(bottom = -0.15,top=1.15)


        plt.margins(0.45)
        #plt.title(f'Probability bounds ({self.identifier})', fontsize=13, pad=8)
        plt.title(f'{self.identifier}', fontsize=13, pad=8)
        
        
        font = {#'family': 'Calibri',
                'color':  'black',
                'weight': 'normal',
                'size': 14,
                'style':'italic'
                }

        if len(x) == 2:

            plt.text(x=-0.13,y= (v['Negative'] - y_error - 0.09), s='Belief', fontdict=font, size=10)
            plt.text(x=-0.2,y= (v['Negative'] + y_error + 0.04), s='Plausibility', fontdict=font, size=10)

            plt.text(x=0.88,y= (v['Positive'] - y_error - 0.09), s='Belief', fontdict=font, size=10)
            plt.text(x=0.79,y= (v['Positive'] + y_error + 0.04), s='Plausibility', fontdict=font, size=10)

        else:

            plt.text(x = -0.014,y= (v[x[0]] - y_error - 0.10), s='Belief', fontdict=font, size=10)
            plt.text(x = -0.023,y= (v[x[0]] + y_error + 0.04), s='Plausibility', fontdict=font, size=10)

        plt.axhline(y = visualise_threshold, color = 'r', linestyle = 'dashed') 

        if export_path is not None:
            plt.savefig(f'{export_path}',facecolor='white', bbox_inches = 'tight')
            
        plt.show()
        
                
    def DecisionMaker(self, visualise = False, return_decision=True, decision_threshold = 0.5, uncertainty_threshold = 0.3):

        """  The decision maker evaluates both, the belief and the uncertainty associated with a single piece of toxicological evidence """
        
        if visualise == True:

            self.visualise_single_evidence(decision_threshold)

        decision_dict = {'Negative': self.belief_plausibility[0],'Positive':self.belief_plausibility[2]}
        uncertainty_col = self.bpa[1]

        for k, val in decision_dict.items():

            if (uncertainty_col >= uncertainty_threshold or val <= decision_threshold):

                self.decision = 'Uncertain'

            else:

                self.decision = k
                break
            
        #print(f'Evidence identified as {self.identifier} of type {self.source.lower()} suggests that that the result is', self.decision.lower(),'!')
        
        if return_decision == True:
            return self.decision 

            ### TO DO:make decisions nummeric

class EvidenceCombinator:
    
    def __init__(self, endpoint, compound=None): 

        self.endpoint = endpoint
        self.bpa = {}
        self.results = {}
        self.weights_dict = {}
        
        if compound is not None:
            self.id = compound

            print(f'INFO - Evidence will be collected for {compound}, focussing on the endpoint "{endpoint}"...')
        else:
            print(f'INFO - Evidence Combinator initiated for the endpoint "{endpoint}"...')
    
    def AddEvidence(self, single_evidence): # from Single_Evidence class
        
        print(f'INFO - Adding evidence with identifier "{single_evidence.identifier}" of type "{single_evidence.source}"...')

        self.bpa[single_evidence.identifier] = single_evidence.bpa
        self.weights_dict[single_evidence.identifier] = single_evidence.weight
        
    def AddEvidenceManually(self, identifier, bpa, weight):
        
        """ This function allows to add evidence without previously applying the QSAR_Single_Evidence class. 
        The following must be defined as identifier: str, bpa: three element numpy array (negative, uncertain, positive), weight: int. """
        
        self.bpa[identifier] = bpa
        self.weights_dict[identifier] = weight
    
    def UpdateWeights(self, new_weights):  
        
        """ This function allows to update weights stored in the evidence combinator, use a dictonary with evidence identifiers as keys and new weights as values. """

        if len(new_weights) == len(self.bpa):
            
            self.weights_dict = new_weights
        else:
            print('Weights not indicated correctly, recheck...')  
            
        print('INFO - Updating weights for the weight of evidence...')
        display(pd.DataFrame(pd.Series(self.weights_dict),columns=['Updated weights']))
    
    def collect(self, df_collect, iterations): 

        collected = 0

        for element in iterations:
            count = 1

            for index, row in df_collect.iterrows():

                count = count * row[element[index]] 

            collected = collected + count

        return collected
            
    def weight_of_evidence(self, dataframe):
        
        try:

            for num, idx in enumerate(dataframe.index):

                arr = np.repeat(dataframe.loc[[idx]].values, self.weights_dict[idx], axis=0)
                col = np.repeat(idx,self.weights_dict[idx] )

                if num == 0:

                    final = arr
                    final_cols = col
                else:

                    final = np.append(final, arr  ,axis = 0)
                    final_cols = np.append(final_cols, col, axis = 0)

            df_woe = pd.DataFrame(final, index=final_cols, columns=dataframe.columns.to_list())

        except Exception:
            print('No weights provided, weight of evidence cannot be applied !!')

        return df_woe
    
    def automatised_rule_selector(self, data):
        
        label = []

        for index, row in data.iterrows():

            threshold_conflict = (row['Positive'] + row['Negative'])/2 
            
            if row['Positive'] > threshold_conflict:
                label.append('p')
                
            if row['Uncertain'] > self.auto_uncertainty_threshold:
                label.append('u')
                
            if row['Negative'] > threshold_conflict:
                label.append('n')
                

        if len(set(label)) == 1:

            rule = 'Dempster'
            comment = 'INFO - Choosing Dempster\'s rule: Agreement between sources and none exceeding uncertainty threshold.'

        elif 'u' in set(label):
            
            rule = 'Yager'
            comment = 'INFO - Choosing Yager\'s rule: Uncertainty threshold exceeded.'
        else: 
            
            rule = 'Inagaki' 
            comment = 'INFO - Choosing Inagaki\'s rule: No agreement between sources.'

        return rule, comment
    
    
    def Combination(self, rule_selection = None, scale_c_inagaki = 1, auto_uncertainty_threshold = 0.3, WoE = False):    # rule_selection from ['Dempster', 'Yager', 'Inagaki','auto'] or None

        """ This function combines evidence using rules based on the Dempster-Shafer theory. The rule_selection options are: 'Dempster', 'Yager', 'Inagaki','auto', if None, all rules will be included in the output. """ 
        
        self.results = {}
        self.auto_uncertainty_threshold = auto_uncertainty_threshold

        df = self.ReturnResults('bpa').copy()

        if WoE:

            df_gpm = self.weight_of_evidence(df)

            print("INFO - Considering individual weights of evidence...")

        else:
            df_gpm = df.copy()

        n_sources = len(df_gpm.index)

        df_gpm.reset_index(inplace=True,drop=True)
        df_gpm.rename(columns={'Positive':'P', 'Uncertain':'U','Negative':'N'}, inplace=True)

        iterations_p = list(itertools.product('PU',repeat=n_sources))[:-1:]
        iterations_n = list(itertools.product('NU',repeat=n_sources))[:-1:]
        iterations_u = list(itertools.product('PN',repeat=n_sources))[1:-1:]

        print("INFO - Computing ground probability masses...")

        gpm_pos = self.collect(df_gpm, iterations_p)
        gpm_neg = self.collect(df_gpm, iterations_n)
        gpm_unc = df_gpm['U'].prod()
        gpm_con = 1 - (gpm_pos + gpm_neg + gpm_unc)
        
        print("INFO - Combining evidence...")

        k_dempster = 1 - gpm_con
        combination_dempster = np.array([gpm_neg/k_dempster, gpm_unc/k_dempster, gpm_pos/k_dempster])


        unc_yager = 1 - gpm_pos - gpm_neg
        combination_yager = np.array([gpm_neg, unc_yager, gpm_pos])

        c = (1 / (1 - gpm_unc - gpm_con)) * scale_c_inagaki
        combination_inagaki = np.array([gpm_neg * (1 + c * gpm_con), (1 + c * gpm_con) * (gpm_unc + gpm_con ) - c * gpm_con, gpm_pos * (1 + c * gpm_con)])
        
        # check if rule selection automatic or not, if not --> assign the rule to the selected one or none

        try:

            if rule_selection == 'auto':
                print("INFO - Automatised rule selection...")
                self.rule, rule_selection_info = self.automatised_rule_selector(df)

            elif (rule_selection in ['Dempster', 'Yager', 'Inagaki'] or rule_selection is None):
                self.rule, rule_selection_info = rule_selection, None

        except Exception:
            print('ERROR - Wrong assignment of rule, please correct!')

        if self.rule is None:

            print("INFO - No rule selected, combining evidence using all rules...")

            self.results['Dempster'] = combination_dempster 
            self.results['Yager'] = combination_yager
            self.results['Inagaki'] = combination_inagaki 

        elif self.rule == 'Dempster':

            self.results['Dempster'] = combination_dempster 

            if rule_selection_info is not None:
                print(rule_selection_info)

        elif self.rule == 'Yager':

            self.results['Yager'] = combination_yager

            if rule_selection_info is not None:
                print(rule_selection_info)

        elif self.rule == 'Inagaki':

            self.results['Inagaki'] = combination_inagaki 

            if rule_selection_info is not None:
                print(rule_selection_info)
    
    
    def ReturnResults(self, selection=None): # selection from ['bpa', 'result', 'Dempster', 'Yager', 'Inagaki'] or None
        
        """" Selecting 'bpa', or 'result' returns the basic probabilty masses or all combination scores, respectively. By selecting a rule name, all the basic probabilty masses together with the specific combination score will be returned."""
        
        if selection == 'bpa':
            return pd.DataFrame(self.bpa, index = ['Negative', 'Uncertain', 'Positive']).T.round(2)
        
        elif selection == 'result':
            return pd.DataFrame(self.results, index = ['Negative', 'Uncertain', 'Positive']).T.round(2)
        
        elif selection in ['Dempster','Yager','Inagaki']:
            return pd.concat([pd.DataFrame(self.bpa, index = ['Negative', 'Uncertain', 'Positive']).T , pd.DataFrame({selection:self.results[selection]},index = ['Negative', 'Uncertain', 'Positive']).T]).round(2)
            
        else:
            return pd.concat([pd.DataFrame(self.bpa, index = ['Negative', 'Uncertain', 'Positive']).T , pd.DataFrame(self.results, index = ['Negative', 'Uncertain', 'Positive']).T]).round(2)

    def Visualise(self, selection=None, export_path=None):    # selection from ['bpa', 'result', 'Dempster', 'Yager', 'Inagaki'] or None

        """ Visualisation of probability bars, selection from ['bpa', 'result', 'Dempster', 'Yager', 'Inagaki'] or None. """
        

        #print(f'INFO - Showing combination results for {self.id}, generated for endpoint "{self.endpoint}"...')

        chosen = self.ReturnResults(selection)
        
        labels = ["Combination result" if item in ['Dempster','Yager','Inagaki'] else item for item in chosen.index ] #[item + str("'s rule") if item in ['Dempster','Yager','Inagaki'] else item for item in chosen.index ]
        
        data = np.array(chosen)    


        data_cum = data.cumsum(axis=1)
        category_names = chosen.columns.to_list()

        category_colors = matplotlib.cm.get_cmap('Blues')(np.linspace(0.15,0.75, data.shape[1]))

        if len (chosen.index) == 1:
            fig, ax = plt.subplots(figsize=(8.5, 1.1))

        else:
            bar_height = 1.1 * (1 + len(chosen.index))
            fig, ax = plt.subplots(figsize=(8.5, bar_height))

        ax.invert_yaxis()
        ax.xaxis.set_visible(False)

        ax.set_xlim(0, np.sum(data, axis=1).max())
        ax.yaxis.set_ticks_position('none')

        text_color = 'black'
        for i, (colname, color) in enumerate(zip(category_names, category_colors)):
            widths = data[:, i]
            starts = data_cum[:, i] - widths
            ax.barh(labels, widths, left=starts, height=0.8,
                    label=colname, color=color)
            plt.yticks(fontsize=14, fontname='Arial',style='italic') #### changes
            xcenters = starts + widths / 2

            r, g, b, _ = color
            for y, (x, c) in enumerate(zip(xcenters, widths)):

                if c != 0.0:
                    ax.text(x, y, str(round(c,2)), ha='center', va='center',
                        color=text_color, fontsize=12,fontname= "Arial") #fontweight="bold"

        ax.legend(ncol=len(category_names), bbox_to_anchor=(-0.015, -0.14),
                  loc='lower left', fontsize=12)

        if selection is None:
            ax.axhline(len(self.ReturnResults('bpa'))-0.5, color ='black', linewidth=0.8, linestyle='--') 
        
        if self.id is not None:
            plt.title(f'Evidence combination ({self.id})', fontsize=15, pad=13)
        else:
            plt.title('Evidence combination', fontsize=15, pad=13)
            
        plt.show()
        
        if export_path is not None:
            fig.savefig(f'{export_path}',facecolor='white', bbox_inches = 'tight')
        
    def DecisionMaker(self, visualise = False, return_decision=True, decision_threshold = 0.5, uncertainty_threshold = 0.3):

        """ Returns a decision based on combined evidence and the user-defined uncertainty and decision thresholds. """
        
        try:
            self.results
        except Exception:
            self.combination('auto')

        if self.rule is not None:

            rule_decision = self.rule

        else:

            print('INFO - No rule selected for combination, running the automatized rule selector.')

            df = self.ReturnResults('bpa').copy()
            rule_decision = self.automatised_rule_selector(df)[0]

        if visualise == True:

            self.visualise(selection=rule_decision)    

        decision_dict = {'Negative': self.results[rule_decision][0],'Positive':self.results[rule_decision][2]}
        uncertainty_col = self.results[rule_decision][1]

        for k, val in decision_dict.items():

            if (uncertainty_col >= uncertainty_threshold or val <= decision_threshold):
                decision = 'Uncertain'

            else:

                decision = k
                break
        
        print(f'INFO - Combining the provided evidence suggests that the result is {decision}!')

        if return_decision == True:
            return decision
            ### TO DO: make decisions nummeric

    def BeliefPlausibilityCombined(self):
        
        try:
            self.results
        except Exception:
            self.combination('auto')

        if self.rule is not None:

            rule_decision = self.rule

        else:

            df = self.ReturnResults('bpa').copy()
            rule_decision = self.automatised_rule_selector(df)[0]
        
        decision_dict = {'Negative': self.results[rule_decision][0],'Positive':self.results[rule_decision][2]}
        uncertainty_col = self.results[rule_decision][1]
        
        
        bel_pos = self.results[rule_decision][2]
        bel_neg = self.results[rule_decision][0]

        pl_pos = 0 if bel_pos == 0 else bel_pos + self.results[rule_decision][1]
        pl_neg = 0 if bel_neg == 0 else bel_neg + self.results[rule_decision][1]
       
        self.belief_plausibility = np.array([bel_neg, pl_neg, bel_pos, pl_pos])
       
        return self.belief_plausibility 
    
    def ShowBeliefPlausibilityCombined(self): # selection includes either of ['bpa', 'bp'], can be left empty  
          
        print('Showing the belief and plausibility for outcomes associated with provided evidence...')
        display(pd.DataFrame({self.endpoint:self.BeliefPlausibilityCombined()}, index = ['Belief (Negative)','Plausibility (Negative)','Belief (Positive)','Plausibility (Positive)']).T.round(2))

        
    def VisualiseBeliefPlausibilityCombination(self, compound_name=None, visualise_threshold = 0.5):
    
        v = {'Negative': self.belief_plausibility[0] + (self.belief_plausibility[1] - self.belief_plausibility[0])/2 ,'Positive': self.belief_plausibility[2] + (self.belief_plausibility[3] - self.belief_plausibility[2])/2}


        y_error = (self.belief_plausibility[1] - self.belief_plausibility[0])/2
        plt.figure(figsize=(3.5,2.75))

        x, y = [], []

        for key, value in v.items():

            if value != 0:

                x.append(key)
                y.append(value)

        plt.errorbar(x, y, yerr = y_error,linestyle="", capsize=6,elinewidth=2,markeredgewidth=2, color='black')#165379

        #plt.xlabel('Outcome', fontsize=15, labelpad=17)
        plt.ylabel('Probability', fontsize=13, labelpad=11)

        plt.xticks(fontsize=13)
        plt.yticks(np.arange(0, 1.05, step=0.1), fontsize=9)
        plt.ylim(bottom = -0.15,top=1.15)


        plt.margins(0.45)
        
        if compound_name is None:
            plt.title('Evidence probability bounds', fontsize=13, pad=8)
        else:
            plt.title(f'Evidence probability bounds ({compound_name})', fontsize=13, pad=8)

        font = {#'family': 'Calibri',
                'color':  'black',
                'weight': 'normal',
                'size': 14,
                'style':'italic'
                }

        if len(x) == 2:
    
            plt.text(x=-0.13,y= (v['Negative'] - y_error - 0.09), s='Belief', fontdict=font, size=10)
            plt.text(x=-0.2,y= (v['Negative'] + y_error + 0.04), s='Plausibility', fontdict=font, size=10)

            plt.text(x=0.88,y= (v['Positive'] - y_error - 0.09), s='Belief', fontdict=font, size=10)
            plt.text(x=0.79,y= (v['Positive'] + y_error + 0.04), s='Plausibility', fontdict=font, size=10)

        else:

            plt.text(x = -0.014,y= (v[x[0]] - y_error - 0.10), s='Belief', fontdict=font, size=10)
            plt.text(x = -0.023,y= (v[x[0]] + y_error + 0.04), s='Plausibility', fontdict=font, size=10)

        plt.axhline(y = visualise_threshold, color = 'r', linestyle = 'dashed') 

        plt.show()
        
