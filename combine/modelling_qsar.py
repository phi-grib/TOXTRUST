import pandas as pd
import os
import numpy as np

import rdkit
from rdkit import RDConfig, Chem
from rdkit.Chem import AllChem, PandasTools, Descriptors, MolFromSmiles, Draw, Crippen, rdMolDescriptors, DataStructs
from rdkit.ML.Descriptors.Descriptors import DescriptorCalculator
from rdkit.ML.Descriptors.MoleculeDescriptors import MolecularDescriptorCalculator

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score

from tqdm import tqdm

class QSAR:
    
    def __init__(self, path_training_series):
        
        self.training = PandasTools.LoadSDF(os.path.join(RDConfig.RDDataDir, path_training_series),molColName='molecule', includeFingerprints=True)
        self.training.dropna(subset=['molecule'], inplace=True)
    

    def compute_descriptors(self, descriptors, series='training'):    # selection from ['MolecularDescriptors', 'MorganFingerprints'] and ['training','test']

        """ Function conserts molecules from the SDfile into descriptors for ML. """
        # TODO: add other descriptor options, properties, rdkit fingerprints etc

        methods = {'MolecularDescriptors': self.md, 'MorganFingerprints': self.fp}

        print(f'INFO - Computing {descriptors} for uploaded {series} dataset...')

        try:
            if series != 'training':
                return methods[descriptors](self.test)

            self.selected_descriptors = descriptors
            self.descriptors = methods[self.selected_descriptors](self.training)

        except Exception:
            print('ERROR - Data not uploaded correctly...')

    def md(self, df):
        
        names = [descriptor[0] for descriptor in Chem.Descriptors._descList if descriptor[0] not in ['Ipc']]
        calculator = MolecularDescriptorCalculator(simpleList=names)

        calculated_descriptors = [calculator.CalcDescriptors(mol) for mol in tqdm(df['molecule'])]

        try:
            scaled = pd.DataFrame(self.scaler.transform(calculated_descriptors), columns=names)
        except Exception:
            self.scaler = StandardScaler()
            scaled = pd.DataFrame(self.scaler.fit_transform(calculated_descriptors), columns=names)

        nan_index = scaled[scaled.isnull().any(axis=1)].index.to_list()

        scaled.drop(nan_index, inplace = True)
        df.drop(nan_index, inplace = True)

        return scaled

    def fp(self, df):
            
        num_objects = len(df)
        xmatrix = np.zeros((num_objects, 2048), dtype=np.int8)

        fp_array = []

        for index, mol in enumerate(tqdm(df['molecule'])):

            fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048, useFeatures=True)

            DataStructs.ConvertToNumpyArray(fp,xmatrix [index])

        fp_data = pd.DataFrame(data=xmatrix, columns=[f'fp_{str(number)}' for number in range(2048)])
        
        nan_index = fp_data[fp_data.isnull().any(axis=1)].index.to_list()
            
        fp_data.drop(nan_index, inplace = True)
        df.drop(nan_index, inplace = True)
        
        return fp_data

    def model(self, model, test_size=0.2):

        X_train, X_test, y_train, y_test = train_test_split(self.descriptors, self.training['result'], random_state=42, test_size=0.2)
        
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        
        model.fit(X_train,y_train)
        
        self.model = model
        print("INFO - Building model...")
        
        
    def get_performance(self, prior = None):
        
        """ Get performance function estimates the """
        
        y_pred = self.model.predict(self.X_test)

        cm = confusion_matrix(self.y_test,y_pred)
        TN = cm[0][0]
        FN = cm[1][0]
        TP = cm[1][1]
        FP = cm[0][1]

        sens = round( TP / (TP+FN),2) # Fraction of the relevant instances that were retrieved # Recall
        spec = round(TN / (TN + FP),2)


        if prior is not None:
            
            print("INFO - Returning updated model performance considering prior probability...")

            PPV = (sens *  prior)/ (sens *  prior + (1 - spec) * (1-prior))
            NPV = (spec *  (1-prior))/ (spec *  (1-prior) + (1 - sens) * prior)  

            return {'performance_pos':PPV,'performance_neg':NPV}

        else:  

            print("INFO - Returning model evaluation metrics ...")

            return {'performance_pos':sens,'performance_neg':spec}

    def predict_proba(self, path_test_series): #Predict class probabilities for X.
        
        """ Predicts percent probability for the test series. """
        
        self.test = PandasTools.LoadSDF(os.path.join(RDConfig.RDDataDir, path_test_series),molColName='molecule', includeFingerprints=True)
        self.test.dropna(subset=['molecule'], inplace=True)
        
        descriptors_test = self.compute_descriptors(self.selected_descriptors, 'test')
        
        print("INFO - Predicting percent probability for the test series...")
        
        return self.model.predict_proba(descriptors_test)
    
    def predict_class(self, path_test_series): #Predict class probabilities for X.
        
        """ Predicts binary labels for the test series. """
        
        self.test = PandasTools.LoadSDF(os.path.join(RDConfig.RDDataDir, path_test_series),molColName='molecule', includeFingerprints=True)
        self.test.dropna(subset=['molecule'], inplace=True)
        
        descriptors_test = self.compute_descriptors(self.selected_descriptors, 'test')       

        print("INFO - Predicting binary class labels for the test series...")
        
        tqdm().close()
        return self.model.predict(descriptors_test)