# TOXTRUST

TOXTRUST is a flexible package allowing for a probablistic evaluation of toxicological evidence as well as for the combination of individual evidence pieces using rigorous rules based on the Dempster-Shafer theory (DST). 

TOXTRUST can currently be used in jupyter notebook. Future versions will allow it's use in the command mode or via GUI.

## Installation 

TOXTRUST can be used in most Windows, Linux or macOS configurations, provided that a suitable execution environment is set up. It is recommended to begin with an installation of the Conda package and the environment manager. A suitable Conda or Anaconda distribution for your operative system can be downloaded from [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html#).

Download the repository:

```bash
git clone https://github.com/phi-grib/TOXTRUST.git
```

Go to the repository directory 

```bash
cd TOXTRUST
```

and create the **"toxtrust" conda environment** with all the dependencies and extra packages:

```bash
conda env create -f environment.yml
```

Once the environment is created type:

```bash
source activate toxtrust
```

to activate the environment.


TOXTRUST must ve installed as a regular Python package. From the "TOXTRUST" directory (note the dot at the end) execute:

```bash
pip install . 
```

If you wish to modify the code for development purposes, use pip with the -e flag, execute: 

```bash
pip install -e .
```

In order to work with the TOXTRUST in Jupyter Notebook, the installation is required. You can install the notebook either in the **"base" conda environment** or in the **"toxtrust" conda environment**. Select the appropriate environment, activate it and run

```bash
pip install notebook
```

Then, although not required, it is also recommended to install the ipykernel within the toxtrust environment in order to correctly set the jupyter notebook kernel. Make sure your **"toxtrust" conda environment** is activated in the terminal and run:

```bash
pip install ipykernel
```

Lastly, to set the kernel run:

```bash
python -m ipykernel install --user --name toxtrust --display-name "Python (toxtrust)"
```

To open jupyter notebook, switch back to the environment in which jupyter is installed and type:

```bash
jupyter notebook
```

## How does it work?

TO BE UPDATED

## Licensing

TOXTRUST was produced at the PharmacoInformatics lab (http://phi.upf.edu), in the framework of the eTRANSAFE project (http://etransafe.eu). eTRANSAFE has received support from IMI2 Joint Undertaking under Grant Agreement No. 777365. This Joint Undertaking receives support from the European Union’s Horizon 2020 research and innovation programme and the European Federation of Pharmaceutical Industries and Associations (EFPIA). Moreover, the project received funding from the European Union’s Horizon 2020 Research and Innovation programme under Grant Agreement No. 964537 (RISK-HUNT3R), which is part of the ASPIS cluster.

Copyright 2023 Karolina Kopanska & Manuel Pastor (karolinaweronika.kopanska@upf.edu / manuel.pastor@upf.edu)

TOXTRUSY is free software: you can redistribute it and/or modify it under the terms of the **GNU General Public License as published by the Free Software Foundation version 3**.

TOXTRUST is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
