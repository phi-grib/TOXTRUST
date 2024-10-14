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
        return False, 'Unable to obtain configuration file.'
    
    return configFile

def configure():
    
    success, message = updateConfig()
    if success:
        
        if os.path.isdir(endpointRepositoryPath()):
            return True, message
        else:
            success, repository_message = endpointRepository()
            if success:
                return True, message + " " + repository_message
            else:
                return False, repository_message

def updateConfig():
    
    try:
        source = os.path.dirname(os.path.dirname(__file__))
        config = os.path.join(source,'config.yaml')
            
        with open(config,'r') as f:
            configFile = yaml.safe_load(f)
            
    except Exception as e:
        return False, e

    if configFile is None:
        return False, 'Unable to obtain configuration file.'

    endpoints = os.path.join(source,'endpoints')

    configFile['toxtrust_repository'] = source
    configFile['endpoints_repository'] = endpoints

    try:
        with open(config, 'w') as yaml_file:
            yaml.dump(configFile, yaml_file)
            return True, 'Configuration updated.'
                
    except Exception as e:
        return False, e

def endpointRepositoryPath(): ## make this happen before you install anything

    configFile = readConfig()

    return configFile['endpoints_repository']

def endpointPath(endpoint):
    
    return os.path.join(endpointRepositoryPath(), endpoint)

def endpointRepository():      
        
    try:
        endpointRepository = endpointRepositoryPath()
        os.mkdir(endpointRepository)
        return True, "Endpoint repository created."
        
    except:
        return False, "Creating repository for endpoints failed."

