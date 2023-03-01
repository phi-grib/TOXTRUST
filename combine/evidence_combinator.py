import pandas as pd
import numpy as np
import math
import itertools

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import display

import matplotlib.pyplot as plt
import os

class Single_Evidence:
    
    def __init__(self, identifier, source, result, reliability, relevance='certain', weight=1):
        
        """ Initiation of Single_Evidence class collecting the most important infomation associated with evidence sources and the results they provide. """
        
        self.identifier = identifier # unique model id
        self.source = source # 'expert','qsar','in vitro', 'positive alert', 'negative alert' for alerts, we need to distinct pos y neg
        self.relevance = relevance # key from dict {'certain':1,'plausible':0.9,'probable':0.75,'equivocal':0.5}
        self.weight = weight # default 1, if other specify using integers
        self.reliability, self.bpa, self.belief_plausibility = self.evidence(source, result, reliability, relevance)
        # reliability = dictionary or list of two values (starting with positive), percent (0 to 100) or point percent (0 to 1)
        
    def check_if_binary(self, r):

        return 'True_Binary' if np.isin(r, [1,0]).all() == True else 'False_Binary'
    
    def evidence(self, source, result, reliability, relevance): 

        print(f'INFO - Processing evidence identified as {self.identifier} of type {source.lower()}.')

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

            data = np.array([neg,pos]).T

        elif evidence_type == 'qualitative_one_class_n': #alert or prediction - predict normal 

            neg = result
            pos = 1 - neg

            data = np.array([neg,pos]).T

        if type(reliability) == dict:

            rel = {'performance_pos': list(reliability.values())[0], 'performance_neg': list(reliability.values())[1]}

        elif type(reliability) == list:

            rel =  {'performance_pos':reliability[0],'performance_neg':reliability[1]}

        else:

            reliability = reliability / 100 if reliability > 1 else reliability

            rel = {'performance_pos':reliability, 'performance_neg':reliability}

        ############## compute bpa's ############## 

        relevance_dict = {'certain':1,'plausible':0.9,'probable':0.75,'equivocal':0.5}

        bpa_pos = data[1] * rel['performance_pos'] * relevance_dict[relevance]
        bpa_neg = data[0] * rel['performance_neg'] * relevance_dict[relevance]
        ignorance = 1 - (bpa_pos + bpa_neg)

        bpa = np.array([bpa_neg, ignorance, bpa_pos])

        ############## compute belief and plausibility ##############

        bel_pos = bpa_pos # only the outcome of intest aka full belief
        bel_neg = bpa_neg

        pl_pos = 0 if bel_pos == 0 else bel_pos + ignorance
        pl_neg = 0 if bel_neg == 0 else bel_neg + ignorance
        
        belief_plausibility = np.array([bel_neg, pl_neg, bel_pos, pl_pos])

        return rel, bpa,  belief_plausibility
    
    def show_components(self, selection=None): # selection includes either of ['bpa', 'bp'], can be left empty  
        
        """" By selecting 'bpa', you will be able to display the basic probabilty assigment for the toxicological evidence piece. By selecting 'bp', you will view belief and probability. By just calling the function, you will see both."""
        
        
        if selection == 'bpa':
            
            print('Showing the basic probability assignments of provided evidence ...')
            display(pd.DataFrame({self.identifier:self.bpa}, index=['Negative','Uncertain','Positive']).T)
            
        elif selection == 'bp':
            
            print('Showing the belief and plausibility for outcomes associated with provided evidence...')
            display(pd.DataFrame({self.identifier:self.belief_plausibility}, index = ['Belief (Negative)','Plausibility (Negative)','Belief (Positive)','Plausibility (Positive)']).T)

        else:
            print('Showing the basic probability assignments of provided evidence...')
            display(pd.DataFrame({self.identifier:self.bpa}, index=['Negative','Uncertain','Positive']).T)
            
            print('Showing the belief and plausibility for outcomes associated with provided evidence...')
            display(pd.DataFrame({self.identifier:self.belief_plausibility}, index = ['Belief (Negative)','Plausibility (Negative)','Belief (Positive)','Plausibility (Positive)']).T)

    
    def visualise_single_evidence(self, visualise_threshold = 0.5):

        v = {'Negative': self.belief_plausibility[0] + (self.belief_plausibility[1] - self.belief_plausibility[0])/2 ,'Positive': self.belief_plausibility[2] + (self.belief_plausibility[3] - self.belief_plausibility[2])/2}

        y_error = self.bpa[1] /2 # assuming equal level of ignorance for each prediction from a constant source
        plt.figure(figsize=(6,4))

        x, y = [], []

        for key, value in v.items():

            if value != 0:

                x.append(key)
                y.append(value)

        plt.errorbar(x, y, yerr = y_error,linestyle="", capsize=10,elinewidth=3,markeredgewidth=4, color='#165379')


        #plt.xlabel('Outcome', fontsize=15, labelpad=17)
        plt.ylabel('Probability', fontsize=16, labelpad=15)

        plt.xticks(fontsize=16)
        plt.yticks(np.arange(0, 1.05, step=0.1), fontsize=13)
        plt.ylim(bottom = -0.15,top=1.15)


        plt.margins(0.45)
        plt.title(f'Evidence probability bounds ({self.identifier})', fontsize=18, pad=12)

        font = {'family': 'Calibri',
                'color':  'black',
                'weight': 'normal',
                'size': 16,
                'style':'italic'
                }

        if len(x) == 2:

            plt.text(x=-0.10,y= (v['Negative'] - y_error - 0.10), s='Belief', fontdict=font, size=16)
            plt.text(x=-0.15,y= (v['Negative'] + y_error + 0.04), s='Plausibility', fontdict=font, size=16)

            plt.text(x=0.91,y= (v['Positive'] - y_error - 0.10), s='Belief', fontdict=font, size=16)
            plt.text(x=0.84,y= (v['Positive'] + y_error + 0.04), s='Plausibility', fontdict=font, size=16)

        else:

            plt.text(x = -0.011,y= (v[x[0]] - y_error - 0.10), s='Belief', fontdict=font, size=16)
            plt.text(x = -0.019,y= (v[x[0]] + y_error + 0.04), s='Plausibility', fontdict=font, size=16)

        plt.axhline(y = visualise_threshold, color = 'r', linestyle = 'dashed') 

        plt.show()
                
    
    def decision_maker(self, visualise = True, default=True):

        """  The decision maker evaluates both, the belief and the uncertainty associated with a single piece of toxicological evidence """
        
        if default == True:
            decision_threshold = 0.5
            uncertainty_threshold = 0.3
            print('INFO - Default settings kept for decision and uncertainty thresholds!')
        else:

            decision_threshold = float(input('USER INPUT - Threshold for decision (number between 0 and 1) --> '))
            uncertainty_threshold = float(input('USER INPUT - Maximum allowed uncertainty level (number between 0 and 1) --> '))

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
            
        print(f'Evidence identified as {self.identifier} of type {self.source.lower()} suggests that that the result is', self.decision.lower(),'!')

class Evidence_Combinator:
    
    def __init__(self, endpoint): 

        self.endpoint = endpoint
        self.bpa = {}
        self.results = {}
        self.weights_dict = {}

        print(f'INFO - Evidence Combinator initiated for the endpoint "{endpoint}"...')
        
    def compound(self, compound_name):
        
        self.id = compound_name

        print(f'INFO - Evidence will be collected and combined for "{compound_name}"...')
    
    def add_evidence(self, single_evidence): # from Single_Evidence class
        
        print(f'INFO - Adding evidence with identifier "{single_evidence.identifier}" of type "{single_evidence.source}"...')

        self.bpa[single_evidence.identifier] = single_evidence.bpa
        self.weights_dict[single_evidence.identifier] = single_evidence.weight
        
    def add_evidence_manually(self, identifier, bpa, weight):
        
        """ This function allows to add evidence without previously applying the QSAR_Single_Evidence class. 
        The following must be defined as identifier: str, bpa: three element numpy array (negative, uncertain, positive), weight: int. """
        
        self.bpa[identifier] = bpa
        self.weights_dict[identifier] = weight
    
    def update_weights(self, new_weights):  
        
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
        
        uncertainty, label = [],[]

        for index, row in data.iterrows():

            threshold_conflict = (row['Positive'] + row['Negative'])/2 
            
            if row['Uncertain'] > 0.5:
                uncertainty = True
            
            if row['Positive'] > threshold_conflict:
                label.append('p')
            else:
                label.append('n')

        if len(set(label)) == 1:
    
            if not uncertainty:
                rule = 'Dempster'
                comment = 'INFO - Choosing Dempster\'s rule: Agreement between sources and none exceeding uncertainty threshold.'
            else:
                rule = 'Yager'
                comment = 'INFO - Choosing Yager\'s rule: Agreement between sources, but uncertainty threshold exceeded.'
        else: 
            rule = 'Dempster' ######'Inagaki' but the rule doesnt work yet because of the formula
            comment = 'INFO - Choosing Inagaki\'s rule: No agreement between sources.'
            
        return rule, comment
    
    
    def combination(self, rule_selection = None, WoE = False):    # rule_selection from ['Dempster', 'Yager', 'Inagaki','auto'] or None

        """ This function combines evidence using rules based on the Dempster-Shafer theory. The rule_selection options are: 'Dempster', 'Yager', 'Inagaki','auto', if None, all rules will be included in the output. """ 
        
        self.results = {}

        try:
            print(f"\nINFO - Evidence combination for: {self.id}")
        except Exception:
            print("\nINFO - Running evidence combination...")

        df = self.return_results('BPA').copy()

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
        gpm_con = self.collect(df_gpm, iterations_u)

        gpm_unc = df_gpm['U'].prod()

        res = gpm_con + gpm_unc

        print("INFO - Combining evidence...")

        k_dempster = gpm_pos + gpm_neg + gpm_unc
        combination_dempster = np.array([gpm_neg/k_dempster, gpm_unc/k_dempster, gpm_pos/k_dempster])


        k_yager = 1 - gpm_pos - gpm_neg
        combination_yager = np.array([gpm_neg, k_yager, gpm_pos])

        combination_inagaki = np.array([np.nan, np.nan, np.nan])

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
            self.results['Inagaki'] = combination_dempster #combination_inagaki

        elif self.rule == 'Dempster':

            self.results['Dempster'] = combination_dempster 

            if rule_selection_info is not None:
                print(rule_selection_info)

        elif self.rule == 'Yager':

            self.results['Yager'] = combination_yager

            if rule_selection_info is not None:
                print(rule_selection_info)

        elif self.rule == 'Inagaki':

            self.results['Inagaki'] = combination_dempster #combination_inagaki

            if rule_selection_info is not None:
                print(rule_selection_info)
    
    
    def return_results(self, selection=None): # selection from ['bpa', 'result', 'Dempster', 'Yager', 'Inagaki'] or None
        
        """" Selecting 'bpa', or 'result' returns the basic probabilty masses or all combination scores, respectively. By selecting a rule name, all the basic probabilty masses together with the specific combination score will be returned."""
        
        if selection == 'bpa':
            return pd.DataFrame(self.bpa, index = ['Negative', 'Uncertain', 'Positive']).T
        
        elif selection == 'result':
            return pd.DataFrame(self.results, index = ['Negative', 'Uncertain', 'Positive']).T
        
        elif selection in ['Dempster','Yager','Inagaki']:
            return pd.concat([pd.DataFrame(self.bpa, index = ['Negative', 'Uncertain', 'Positive']).T , pd.DataFrame({selection:self.results[selection]},index = ['Negative', 'Uncertain', 'Positive']).T])
            
        else:
            return pd.concat([pd.DataFrame(self.bpa, index = ['Negative', 'Uncertain', 'Positive']).T , pd.DataFrame(self.results, index = ['Negative', 'Uncertain', 'Positive']).T])

    def visualise(self, selection=None): # selection from ['bpa', 'result', 'Dempster', 'Yager', 'Inagaki'] or None
        
        """ Visualisation of probability bars, selection from ['bpa', 'result', 'Dempster', 'Yager', 'Inagaki'] or None. """
        
        try:
            print(f'INFO - Showing results for: {self.id}')
        except Exception:
            print('INFO - Showing results for added evidence...')

        chosen = self.return_results(selection)

        labels = chosen.index
        data = np.array(chosen)    

        data_cum = data.cumsum(axis=1)
        category_names = chosen.columns.to_list()

        category_colors = matplotlib.cm.get_cmap('RdYlGn')(np.linspace(0.8,0.20, data.shape[1]))

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

        ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
                  loc='lower left', fontsize=12)

        plt.show()
        
    def decision_maker(self, visualise = True, default = True):

        """ Returns a decision based on combined evidence and the user-defined uncertainty and decision thresholds. """
        
        if default:
            decision_threshold = 0.5
            uncertainty_threshold = 0.3
        else:

            decision_threshold = float(input('USER INPUT - Threshold for decision making (number between 0 and 1) --> '))
            uncertainty_threshold = float(input('USER INPUT - Maximum allowed uncertainty level (number between 0 and 1) --> '))

        try:
            self.results
        except Exception:
            self.combination('auto')

        if self.rule is not None:

            rule_decision = self.rule

        else:

            print('INFO - No rule selected for combination, running the automatized rule selector.')

            df = self.return_results('bpa').copy()
            rule_decision = self.automatised_rule_selector(df)[0]

        if visualise == True:

            self.visualise(selection=rule_decision)    

        decision_dict = {'Negative': self.results[rule_decision][0],'Positive':self.results[rule_decision][2]}
        uncertainty_col = self.results[rule_decision][1]

        for k, val in decision_dict.items():

            if (uncertainty_col >= uncertainty_threshold or val <= decision_threshold):
                self.decision = 'Uncertain'

            else:

                self.decision = k
                break

        print(f'INFO - The collected evidence suggests that that the result is {self.decision.lower()}','!')
        
        
        
        