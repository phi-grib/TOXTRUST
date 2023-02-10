# Dempster-Shafer theory based evidence combinator

The dst_evidence_combinator is a flexible package allowing for a probablistic evaluation of toxicological evidence as well as for combination of individual evidence pieces using rigorous rules based on the Dempster-Shafer theory (DST). The dst_evidence_combinator was developed within the eTRANSAFE (http://etransafe.eu) project. 

The dst_evidence_combinator can currently be used in jupyter notebook. Future versions will allow it's use in the command mode. 

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

## Main features

TODO

- Processing of qsar predicions / toxicological evidence pieces of different types. The single evidence classes require user input that is later translated into basic probability masses, and the degrees of Belief and Plausibility.

- Combining evidence using DST based rules. The evidence combinator classes process the collected evidence in a user-defined way. Elements like Weight of Evidence and .... can be considered. 


## Licensing

The dst_evidence_combinator was produced at the PharmacoInformatics lab (http://phi.upf.edu), in the framework of the eTRANSAFE project (http://etransafe.eu). eTRANSAFE has received support from IMI2 Joint Undertaking under Grant Agreement No. 777365. This Joint Undertaking receives support from the European Union’s Horizon 2020 research and innovation programme and the European Federation of Pharmaceutical Industries and Associations (EFPIA). Moreover, the project received funding from the European Union’s Horizon 2020 Research and Innovation programme under Grant Agreement No. 964537 (RISK-HUNT3R), which is part of the ASPIS cluster.

Copyright 2023 Manuel Pastor (karolinaweronika.kopanska@upf.edu)

The dst_evidence_combinator is free software: you can redistribute it and/or modify it under the terms of the **GNU General Public License as published by the Free Software Foundation version 3**.

dst_evidence_combinator is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with Flame. If not, see <http://www.gnu.org/licenses/>.
