# TOXTRUST

TOXTRUST is a flexible package allowing for a probablistic evaluation of toxicological evidence as well as for the combination of individual evidence pieces using rigorous rules based on the Dempster-Shafer theory (DST). 

TOXTRUST can currently be used in jupyter notebook. Future versions will allow it's use in the command mode or via GUI.

## Installation 

The dst_evidence_combinator can be used in most Windows, Linux or macOS configurations, provided that a suitable execution environment is set up. It is recommended to begin with an installation of the Conda package and the environment manager. A suitable Conda or Anaconda distribution for your operative system can be downloaded from [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html#).

Download the repository:

```bash
git clone https://github.com/phi-grib/dst_evidence_combinator.git
```

Go to the repository directory 

```bash
cd dst_evidence_combinator
```

and create the **"dst" conda environment** with all the dependencies and extra packages:

```bash
conda env create -f environment.yml
```

Once the environment is created type:

```bash
source activate dst
```

to activate the environment.


The dst_evidence_combinator must ve installed as a regular Python package. From the "dst_evidence_combinator" directory (note the dot at the end) execute:

```bash
pip install . 
```

If you wish to modify the code for development purposes, use pip with the -e flag, execute: 

```bash
pip install -e .
```

In order to work with the dst_eviedence_combinator in Jupyter Notebook, the installation is required. You can install the notebook either in the **"base" conda environment** or in the **"dst" conda environment**. Select the appropriate environment, activate it and run

```bash
pip install notebook
```

Then, although not required, it is also recommended to install the ipykernel within the dst environment in order to correctly set the jupyter notebook kernel. Make sure your **"dst" conda environment** is activated in the terminal and run:

```bash
pip install ipykernel
```

Lastly, to set the kernel run:

```bash
python -m ipykernel install --user --name dst --display-name "Python (dst)"
```

To open jupyter notebook, switch back to the environment in which jupyter is installed and type:

```bash
jupyter notebook
```

## How does it work?

TOXTRUST is subdivided into three modules: “libraries”, “modelling_qsar”, and “evidence_combinator”. The first stores the libraries necessary for the execution of the integrated functions. The QSAR modelling module provides simple solution in situations, where QSAR model predictions are required, but the model building process is too cumbersome. It greatly simplifies QSAR model training, the computation of reliability metrics, the generation of predictions for the test compound, and the transformation of the generated data into the DST-format. Lastly, the evidence_combinator constitutes the core of the programme and contains the whole range of relevant functions underlying the DST, adjusted to toxicological assessment purposes. With regard to the structure, the combinator module is further divided into two classes, including the “SingleEvidence” and the “EvidenceCombinator” class, both of which can be seen as systems that bundle data and functionality together. Objects of the class, called instances, are initialised by defining the class-specific variables (inserting data required by the class). 

The *SingleEvidence* class collects and processes information associated with single evidence bodies provided by the user. A specific set of variables is required to initialise a new object of this class. Additionally, the set of variables was extended to allow users for grading and weighting the evidence in line with their personal opinion, as opposed to relying on the results and reliability scores, only. A summary of variables accepted by the SingleEvidence class is provided in the table below. 

| Variable name | Status   | Definition                                                                                                                                                                                                             | Input as       | Input options                                                                                                                                      |
|---------------|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| identifier    | required | unique identification of the body of evidence                                                                                                                                                                          | string         | arbitrary expression                                                                                                                               |
| source        | required | type of the body of evidence                                                                                                                                                                                           | string         | one of the following: 'expert','qsar','in vitro', 'positive alert', 'negative alert'                                                               |
| result        | required | result generated by the body of evidence                                                                                                                                                                               | number         | a) a single number always in respect to the positive class (1 means positive)                                                                      |
|               |          |                                                                                                                                                                                                                        | number         | b) a single probability score in respect to the positive class (e.g.: 0.75 probability of being positive)                                          |
|               |          |                                                                                                                                                                                                                        | list           | c) list with two probability scores collected for the negative and positive results (starting with negative)                                       |
| reliability   | required | reliability score of the body of evidence                                                                                                                                                                              | number         | a) a single number representing the accuracy score, on the scale from 0 to 100 or from 0 to 1                                                      |
|               |          |                                                                                                                                                                                                                        | dictionary     | b) a dictionary with two values, on the scale from 0 to 1, representing the negative and the positive reliability scores  (starting with negative) |
|               |          |                                                                                                                                                                                                                        | list           | c) a list with two values, on the scale from 0 to 1, representing the negative and the positive reliability scores (starting with negative)        |
| relevance     | optional | expert-defined relevance term linking the evidence source (not the result itself) to the assessment question; the default setting is “certain” meaning that the evidence source is completely relevant to the endpoint | string         | a) 'certain' equivalent to 1                                                                                                                       |
|               |          |                                                                                                                                                                                                                        | string         | b) 'probable' equivalent to 0.9                                                                                                                    |
|               |          |                                                                                                                                                                                                                        | string         | c) 'plausible' equivalent to 0.75                                                                                                                  |
|               |          |                                                                                                                                                                                                                        | string         | d) 'equivocal' equivalent to 0.5                                                                                                                   |
|               |          |                                                                                                                                                                                                                        | string         | e) 'doubted' equivalent to 0.25                                                                                                                    |
|               |          |                                                                                                                                                                                                                        | string         | f) 'improbable' equivalent to 0.1                                                                                                                  |
|               |          |                                                                                                                                                                                                                        | string         | g) 'impossible' equivalent to 0                                                                                                                    |
| weight        | optional | expert-defined weight of the evidence body, as compared to other evidence bodies considered for combination; the default setting is 1                                                                                  | integer number | arbitrary integer number (e.g.: 1, 2, 3, …)                                                                                                        |



The code for evidence processing and combination as well as the list of required libraries are stored in the combine-subpackage, which must be loaded first. Then, each piece of information derived from an independent body of evidence is handled separately by the “Single_Evidence” class. The initiation of this class required providing the following information:

* Identifier
The Identifier is the unique name that will be used further to refer to each particular instance of the “Single_Evidence” class.

*	Source
The Source refers to the origin of the data, including the following options: “expert”, “QSAR”, “in vitro”, “positive alert”, “negative alert”, whereby the distinction between positive and negative alerts is essential for the correct processing of the provided data. 

*	Result 
The Result parameter represents the experimental value derived from the evidence body. It can be used in a singular form (one value) or binary form (two values). While for the singular form, scale allows to use one value, always referring to the positive result, indicating percent (0 to 100) or point percent (0 to 1), or a binary outcome (0 or 1), the binary form additionally requires the provided values to sum to 1. 

*	Reliability 
Reliability score associated with the evidence body. Provided in the form of a dictionary or a list with two values, the first always being the score associated with the positive result. Two value-scales are allowed, the percent (0 to 100) or point percent (0 to 1).

*	Relevance
The “Relevance” is an additional parameter, allowing the experts to provide additional estimates of the relevance of the particular evidence piece for the assessment question. Options include the four dictionary keys and their associated values: “certain”: 1, “plausible” : 0.9, “probable” : 0.75, and  “equivocal” : 0.5. This parameter is soft-coded using the “certain” value, therefore the reliability score will not be accounted for to scale the provided probabilities, unless changed accordingly. 

*	Weight
While the Relevance parameter facilitates scaling the provided probabilities, the weight parameter gives users the possibility to weight the evidence pieces, using integer numbers like 1,2,3 … etc. 

After the information is provided and the cell is run, the underlying functions process the evidence accordingly, without the need of any user-interactions. Values like the bpa’s, the degrees of Belief and Plausibilty are automatically computed and stored in each instance of the class, separately. Additional functions like “return_results” and “visualise” allow for printing the results in an organised, tabular format and visualising the bonds of Belief and Plausibility, respectively. When relying one a single source of evidence, by running the function “decision-maker”, the code allows to make threshold-based decisions.

Evidence combination can be started after all evidence pieces are processed and take on the form of the “Single_Evidence” class instance. Alternatively, evidence can also be added manually by running the function "add_evidence_manually()", thereby providing all required information. The “Evidece_Combinator” class is then initiated by providing a name, in a string format. All previously processed single evidence pieces are then added to the combinator class using the function “add_evidence(“Single_Evidence”-class instance)”. Next, the combination is performed by running the "combination()" function. The example notebooks demonstrate in detail how this can be done.

## Licensing

The dst_evidence_combinator was produced at the PharmacoInformatics lab (http://phi.upf.edu), in the framework of the eTRANSAFE project (http://etransafe.eu). eTRANSAFE has received support from IMI2 Joint Undertaking under Grant Agreement No. 777365. This Joint Undertaking receives support from the European Union’s Horizon 2020 research and innovation programme and the European Federation of Pharmaceutical Industries and Associations (EFPIA). Moreover, the project received funding from the European Union’s Horizon 2020 Research and Innovation programme under Grant Agreement No. 964537 (RISK-HUNT3R), which is part of the ASPIS cluster.

Copyright 2023 Karolina Kopanska & Manuel Pastor (karolinaweronika.kopanska@upf.edu / manuel.pastor@upf.edu)

The dst_evidence_combinator is free software: you can redistribute it and/or modify it under the terms of the **GNU General Public License as published by the Free Software Foundation version 3**.

dst_evidence_combinator is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
