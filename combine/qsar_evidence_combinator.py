import pandas as pd
import numpy as np
import math
import itertools

import matplotlib
import matplotlib.pyplot as plt
from IPython.display import display

import matplotlib.pyplot as plt
import os

class QSAR_Single_Evidence:
    
    def __init__(self, identifier, prediction, reliability, relevance='certain', weight=1):
        
        """ Initiation of QSAR_Single_Evidence class collecting the most important infomation associated with the model and its predictions. """
        
        self.identifier = identifier # unique model id
        self.relevance = relevance # key from dict {'certain':1,'plausible':0.9,'probable':0.75,'equivocal':0.5}
        self.weight = weight # default 1, if other specify using integers
        self.reliability, self.bpa, self.belief_plausibility = self.qsar_evidence(prediction, reliability, relevance) 
        # reliability = dictionary or list of two values (starting with positive), percent (0 to 100) or point percent (0 to 1)
        
    def qsar_evidence(self, prediction, reliability, relevance=None):
        
        print(f'INFO - Processing evidence from model identified as "{self.identifier}"...')

        if not np.isin(prediction, [1,0]).all():

            data = prediction

        else:

            pos = prediction
            neg = 1 - pos

            data = np.array([neg,pos]).T

        if type(reliability) == dict:
            
            rel = {'performance_pos': list(reliability.values())[0],'performance_neg': list(reliability.values())[1]}

        elif type(reliability) == list:

            rel =  {'performance_pos':reliability[0],'performance_neg':reliability[1]}

        else:

            reliability = reliability / 100 if reliability > 1 else reliability
            rel = {'performance_pos':reliability, 'performance_neg':reliability}

        relevance_dict = {'certain':1,'plausible':0.9,'probable':0.75,'equivocal':0.5}

        ############## compute basic probability masses ##############
        
        bpa_pos = data[:,1] * rel['performance_pos'] * relevance_dict[relevance]  # TODO: add a way to completely remove evidence
        bpa_neg = data[:,0] * rel['performance_neg'] * relevance_dict[relevance]
        ignorance = 1 - (bpa_pos + bpa_neg)

        bpa = np.array([bpa_neg,ignorance,bpa_pos])

        ############## compute belief and plausibility ##############

        bel_pos = bpa_pos # only the outcome of interest aka full belief
        bel_neg = bpa_neg

        bel_pos = bpa_pos # only the outcome of interest aka full belief
        bel_neg = bpa_neg

        pl_pos = [(bel_pos[p] + ignorance[p]) if bel_pos[p] != 0 else 0 for p in range(len(prediction))]
        pl_neg = [(bel_neg[n] + ignorance[n]) if bel_neg[n] != 0 else 0 for n in range(len(prediction))]

        belief_plausibility = np.array([bel_neg, pl_neg, bel_pos, pl_pos])
        
        return rel, bpa,  belief_plausibility
    
    def test(self, ids = None, test_set = None):
        
        """ Function to define testset and provdide more information """
    
        if ids is not None:
            
            self.ids = [str(id_single) for id_single in ids]
        
        if test_set is not None:
            
            self.test_set = test_set
            
            if ids is None:
            
                self.ids = test_set['ID']
    
    def qsar_show_components(self, selection=None):    # selection includes either of ['bpa', 'bp'], can be left empty 

        """" By selecting 'bpa', you will be able to display the basic probabilty assigment for the model. By selecting 'bp', you will view belief and probability. By just calling the function, you will see both."""
        
        try:
            cols = self.ids
        except Exception:
            cols = np.arange(len(self.bpa))

        if selection == 'bpa':

            print('Showing the basic probability assignments of provided evidence ...')
            display(pd.DataFrame(self.bpa, columns=cols, index=['Negative','Uncertain','Positive']).T)

        elif selection == 'bp':

            print('Showing the belief and plausibility for outcomes associated with provided evidence...')
            display(pd.DataFrame(self.belief_plausibility, columns=cols,  index = ['Belief (Negative)','Plausibility (Negative)','Belief (Positive)','Plausibility (Positive)']).T)

        else:
            print('Showing the basic probability assignments of provided evidence...')
            display(pd.DataFrame(self.bpa, columns=cols, index=['Negative','Uncertain','Positive']).T)

            print('Showing the belief and plausibility for outcomes associated with provided evidence...')
            display(pd.DataFrame(self.belief_plausibility, columns=cols,  index = ['Belief (Negative)','Plausibility (Negative)','Belief (Positive)','Plausibility (Positive)']).T)
   
        
    def qsar_visualise_single_evidence(self, compound = None, visualise_threshold = 0.5):
        
        if compound in np.arange(self.belief_plausibility.shape[1]):
            k = int(compound) 
            self.qsar_visualise_execute(k, visualise_threshold)
        elif compound is not None:
            
            try:
                k = self.ids.index(compound)
                self.qsar_visualise_execute(k, visualise_threshold)
            except Exception:
                print('Testset or IDs not correctly provided to execute, please check!')
        else:
            for k in range (self.belief_plausibility.shape[1]):
                self.qsar_visualise_execute(k, visualise_threshold)
        
    def qsar_visualise_execute(self, k, visualise_threshold):
        
        v = {'Negative': self.belief_plausibility[0][k] + (self.belief_plausibility[1][k] - self.belief_plausibility[0][k])/2 ,'Positive': self.belief_plausibility[2][k] + (self.belief_plausibility[3][k] - self.belief_plausibility[2][k])/2}

        y_error = self.bpa[1][k] /2 # assuming equal level of ignorance for each prediction from a constant source
                                    # this is different from conformal prediction where each pred has different confidence is different

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
        plt.title(f'Probability bounds ID: {str(k)}', fontsize=18,pad=12)

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
                
    def qsar_decision_maker(self, compound = None, visualise = False, default = True):

        """  The decision maker evaluates both, the belief and the uncertainty associated with a single piece of toxicological evidence """

        if default == True:
            decision_threshold = 0.5
            uncertainty_threshold = 0.3
            print('INFO - Default settings kept for decision and uncertainty thresholds!')
        else:

            decision_threshold = float(input('USER INPUT - Threshold for decision (number between 0 and 1) --> '))
            uncertainty_threshold = float(input('USER INPUT - Maximum allowed uncertainty level (number between 0 and 1) --> '))

        if compound in np.arange(self.belief_plausibility.shape[1]):
            k = int(compound)
            print(f'INFO - Making an individual decision for a compound {k}, the result is {self.decision_execute(k, decision_threshold, uncertainty_threshold, visualise).lower()}!')

        elif compound is not None:
            try:
                k = self.ids.index(compound)
                print(f'INFO - Making an individual decision for a compound {k}, the result is {self.decision_execute(k, decision_threshold, uncertainty_threshold, visualise).lower()}!')
            except Exception:
                print('ERROR - Testset or IDs not correctly provided to execute, please check!')
        else:
            print()
            print('INFO - Making decisions for all compounds from the test set!')
            self.decisions = [] 
            for k in range (self.belief_plausibility.shape[1]):
                decision = self.decision_execute(k, decision_threshold,uncertainty_threshold, visualise)
                self.decisions.append(decision)
        
    def decision_execute(self, k, decision_threshold, uncertainty_threshold,visualise):   
        
        if visualise == True:

            self.qsar_visualise_execute(k, decision_threshold)  

        decision_dict = {'Negative': self.belief_plausibility[0][k],'Positive':self.belief_plausibility[2][k]}
        uncertainty_col = self.bpa[1][k]

        for k, val in decision_dict.items():

            if (uncertainty_col >= uncertainty_threshold or val <= decision_threshold):
                
                decision = 'Uncertain'
                
            else:

                decision = k
                break
        return decision

    def merge_desicions_with_test(self):
        
        try:
            test_set_decisions = self.test_set.copy()
            test_set_decisions['decisions'] = self.decisions

            return test_set_decisions

        except Exception:
            print("ERROR - Test set not provided or decisions not made correctly !!")

class QSAR_Evidence_Combinator:
    
    def __init__(self, endpoint): 
        
        self.endpoint = endpoint
        self.bpa = {}
        self.results = {}
        self.weights_dict = {}
        self.rules = {}

        print(f'INFO - QSAR Evidence Combinator initiated for the endpoint "{endpoint}"...')
        
    def upload_test(self, test_set = None, name_col = 'ID'):

        """ Function to define the test set and provdide more information """

        self.test_set = test_set

        self.ids = test_set[name_col] if name_col == 'ID' else test_set.index.values
        
        print('INFO - Test set defined...')

    def add_evidence(self, single_evidence):
        
        print(f'INFO - Adding evidence from QSAR model with identifier {single_evidence.identifier} ...')

        self.bpa[single_evidence.identifier] = pd.DataFrame(single_evidence.bpa, index = ['Negative', 'Uncertain', 'Positive']).T
        self.weights_dict[single_evidence.identifier] = single_evidence.weight
        
    def add_evidence_manually(self, identifier, bpa, weight):
        
        """ This function allows to add evidence without previously applying the QSAR_Single_Evidence class. 
        The following must be defined as identifier: str, bpa: three element numpy array (negative, uncertain, positive), weight: int. """
        
        self.bpa[identifier] = pd.DataFrame(bpa, index = ['Negative', 'Uncertain','Positive']).T
        self.weights_dict[identifier] = weight
       
    def update_weights(self, new_weights):  
        
        """ This function allows to update weights stored in the evidence combinator, use a dictonary with evidence identifiers as keys and new weights as values. """

        try:
            if len(new_weights) == len(self.bpa):
            
                self.weights_dict = new_weights
                
        except Exception:
            print('ERROR - Weights not indicated correctly, recheck...')  
            
        print('INFO - Updating weights for the weight of evidence...')
        display(pd.DataFrame(pd.Series(self.weights_dict),columns=['Updated weights']))
    
    def restructure_evidence(self):
        
        self.results_restructured = {}

        if all(len(v) == len(self.ids) for v in self.bpa.values()):

            for n in range(len(self.ids)):
                df_dict = {key: self.bpa[key].iloc[n,:] for key in self.bpa.keys()}
                df = pd.DataFrame(df_dict).T

                self.results_restructured[self.ids[n]] = df
        else:
            print('INFO - Provided evidence not of same length, breaking out...')

        return self.results_restructured

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
    

    def combination(self, rule_selection = None, WoE = False): ### automatized_selection = False (this would allow for checking the agreement)

        df_dict = self.restructure_evidence()

        i =  0
        for key, value in df_dict.items(): # key = mol name, value, the df with predictions from different sources
            
            #print("\nINFO - Evidence combination for molecule: {}".format(key))

            df = value

            if WoE:

                df_gpm = self.weight_of_evidence(df)

                if i == 0:
                    print("INFO - Considering individual weights of evidence...")

            else:
                df_gpm = df.copy()

            n_sources = len(df_gpm.index)

            df_gpm.reset_index(inplace=True,drop=True)
            df_gpm.rename(columns={'Positive':'P', 'Uncertain':'U','Negative':'N'}, inplace=True)

            iterations_p = list(itertools.product('PU',repeat=n_sources))[:-1:]
            iterations_n = list(itertools.product('NU',repeat=n_sources))[:-1:]
            iterations_u = list(itertools.product('PN',repeat=n_sources))[1:-1:]

            if i == 0:
                print("INFO - Computing ground probability masses...")

            gpm_pos = self.collect(df_gpm, iterations_p)
            gpm_neg = self.collect(df_gpm, iterations_n)
            gpm_con = self.collect(df_gpm, iterations_u)

            gpm_unc = df_gpm['U'].prod()

            if i == 0:    
                print("INFO - Combining evidence...")

            ### first dempster's combination
            k_dempster = gpm_pos + gpm_neg + gpm_unc

            combination_dempster = pd.Series(data={'Negative':gpm_neg/k_dempster, 'Uncertain':gpm_unc/k_dempster, 'Positive':gpm_pos/k_dempster}, name='Dempster',dtype='float64')
            ### second yager's combination
            k_yager = 1 - gpm_pos - gpm_neg

            combination_yager = pd.Series(data={'Negative':gpm_neg, 'Uncertain':k_yager,'Positive':gpm_pos}, name='Yager',dtype='float64')

            ### third Inagaki's combination
            combination_inagaki = pd.Series(data={'Negative':np.nan, 'Uncertain':np.nan,'Positive':np.nan}, name='Inagaki',dtype='float64')

            # check if rule selection automatic or not, if not --> assign the rule to the selected one or none

            try:
                if rule_selection == 'auto':
                    if i == 0:
                        print("INFO - Automatised rule selection...")
                    rule, rule_selection_info = self.automatised_rule_selector(df)

                elif (rule_selection in ['Dempster', 'Yager', 'Inagaki'] or rule_selection is None):
                    self.rule, rule_selection_info = rule_selection, None
            except Exception:
                print('ERROR - Wrong assignment of rule, please correct!')

            # continue with the info from above!
            if self.rule is None:

                result = pd.DataFrame([combination_dempster,combination_yager]) ### leave out Inagaki for now
                if i == 0:
                    print("INFO - No rule selected, combining evidence using all rules...")

            elif self.rule == "Dempster":

                result = pd.DataFrame([combination_dempster])

                if rule_selection_info is not None and i == 0:
                    print(rule_selection_info)

            elif self.rule == "Yager":

                result = pd.DataFrame([combination_yager])

                if rule_selection_info is not None and i == 0:
                    print(rule_selection_info)

            elif self.rule == "Inagaki":

                result = pd.DataFrame([combination_inagaki])

                if rule_selection_info is not None and i == 0:
                    print(rule_selection_info)

            self.results[key] = result
            self.rules[key] = self.rule

            i += 1
    
    def return_results(self, selection=None, mol=None): # selection from ['bpa', 'result', 'Dempster', 'Yager', 'Inagaki'] or None

        """" Selecting 'bpa', or 'result' returns the basic probabilty masses or all combination scores, respectively. By selecting a rule name, all the basic probabilty masses together with the specific combination score will be returned."""
        
        
        if selection == 'bpa':

            try:
                self.results_restructured

            except Exception:
                self.restructure_evidence()

            if mol is not None:
                return self.results_restructured[mol]

            else:
                return self.results_restructured


        elif selection == 'result':

            try:
                self.results

            except Exception:
                self.combination('auto')

            return self.results[mol] if mol is not None else self.results
        elif selection in ['Dempster','Yager','Inagaki']:

            return pd.concat([self.results_restructured[mol],self.results[mol].loc[[selection]]])

        elif selection is None:

            try:
                all_dict = {key: pd.concat([self.results_restructured[key], self.results[key]]) for key in self.results.keys()}
                
                return all_dict[mol] if mol is not None else all_dict
            except Exception:
                print('ERROR - Combination not performed, nothing to return...')

    def visualise(self, selection=None, mol=None): 
        
        """ Visualisation of probability bars, selection from ['bpa', 'result', 'Dempster', 'Yager', 'Inagaki'] or None. For one molecule, if None, for the whole test set. """
        
        result = self.return_results(selection, mol)

        if type(result) == dict:
            for molecule, df in result.items(): 
                self.visualise_execute(df,molecule)
        else:
            self.visualise_execute(result, mol)

    def visualise_execute(self, df, molecule): 
        
        print(f'INFO - Showing results for: {molecule}')

        labels = df.index
        data = np.array(df)    

        data_cum = data.cumsum(axis=1)
        category_names = df.columns.to_list()

        category_colors = matplotlib.cm.get_cmap('RdYlGn')(np.linspace(0.80,0.20, data.shape[1]))

        if len (df.index) == 1:
            fig, ax = plt.subplots(figsize=(8.5, 1.1))

        else:
            bar_height = 1.1 * (1 + len(df.index))
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
        
    def decision_maker(self, visualise = True, default = True, mol = None): 
        
        """ Returns a decision based on combined evidence and the user-defined uncertainty and decision thresholds. If molecule is not defined, decisions are made for the whole test set. """
        
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

        if mol is not None:
            print(f'INFO - The collected evidence for {mol} suggests that that the result is {self.decision_execute(visualise, mol, decision_threshold, uncertainty_threshold)}','!')
        else:
            self.decisions = [self.decision_execute(i, visualise,molecule,decision_threshold, uncertainty_threshold) for i, molecule in enumerate(self.results)]
            print('INFO - Decisions computed and stored for collected evidence!')

    def decision_execute(self,i, visualise, mol, decision_threshold, uncertainty_threshold):

        if self.rules[mol] is not None:

            rule_decision = self.rules[mol]

        else:

            df = self.results_restructured[mol]
            rule_decision = self.automatised_rule_selector(df)[0]

            if i == 0:

                print(f"INFO - No rule selected for combination, automatically selected {rule_decision}\'s rule.")

        if visualise:

            self.visualise(selection = rule_decision, mol=mol)

        decision_mol = self.results[mol]  

        decision_dict = {'Negative': decision_mol.loc[rule_decision][0],'Positive':decision_mol.loc[rule_decision][2]}
        uncertainty_col = decision_mol.loc[rule_decision][1]

        for k, val in decision_dict.items():

            if (uncertainty_col >= uncertainty_threshold or val <= decision_threshold):
                
                decision = 'Uncertain'

            else:

                decision = k
                break
            
        return decision

    def decision_test(self):
                  
        test_decisions = self.test_set.copy()

        try:
            test_decisions['decisions'] = self.decisions

        except Exception:
            self.decision_maker(self, visualise = False, default = True, mol = None)
            test_decisions['decisions'] = self.decisions

        return test_decisions
        
        
        