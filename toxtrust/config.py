import os
import yaml


def toxtrustPath():
    
    return os.path.dirname(os.path.dirname(__file__))

def readConfig():
    
    try:
        source = os.path.dirname(os.path.dirname(__file__))
        config = os.path.join(source,'config.yaml')
        
        with open(config,'r') as f:
            configFile = yaml.safe_load(f)
            
    except Exception as e:
        return False, e

    if configFile is None:
        return False, 'Unable to obtain configuration file'
    
    return configFile

def updateConfig():
    
    try:
        source = os.path.dirname(os.path.dirname(__file__))
        config = os.path.join(source,'config.yaml')
            
        with open(config,'r') as f:
            configFile = yaml.safe_load(f)
            
    except Exception as e:
        return False, e

    if configFile is None:
        return False, 'Unable to obtain configuration file'

    endpoints = os.path.join(source,'endpoints')

    configFile['toxtrust_repository'] = source
    configFile['endpoints_repository'] = endpoints

    try:
        with open(config, 'w') as yaml_file:
            yaml.dump(configFile, yaml_file)
                
    except Exception as e:
        return False, e

def endpointRepositoryPath(): ## make this happen before you install anything

    configFile = readConfig()

    return configFile['endpoints_repository']

def endpointPath(endpointName):
    
    return os.path.join(endpointRepositoryPath(), endpointName)

def endpointRepository():      
        
    try:
        endpointRepository = endpointRepositoryPath()
        os.mkdir(endpointRepository)
        
    except:
        return False, "Creating repository for endpoints failed"

