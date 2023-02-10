
import pandas as pd
import numpy as np

import os
import math
import itertools

import rdkit
from rdkit import RDConfig, Chem
from rdkit.Chem import AllChem, PandasTools, Descriptors, MolFromSmiles, Draw, Crippen, rdMolDescriptors, DataStructs
from rdkit.ML.Descriptors.Descriptors import DescriptorCalculator
from rdkit.ML.Descriptors.MoleculeDescriptors import MolecularDescriptorCalculator

import sklearn
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score

import matplotlib
import matplotlib.pyplot as plt
import xlsxwriter
from IPython.display import display

from tqdm import tqdm