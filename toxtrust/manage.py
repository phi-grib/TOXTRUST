import os
import yaml
import shutil
import string
import random 

from toxtrust.config import endpointPath, toxtrustPath, endpointRepositoryPath
from toxtrust.endpoint import Endpoint

def createEndpoint(endpointName):
    
    if not endpointName:
        return False, 'Empty endpoint name'

    # importlib does not allow using 'test' and issues a misterious error when we
    # try to use this name. This is a simple workaround to prevent creating ranames 
    # with this name 
    
    if endpointName == 'test':
        return False, 'The name "test" is disallowed, please use any other name' 
    
    ndir = endpointPath(endpointName)
    
    if os.path.isdir(ndir):
        return False, f'Endpoint {endpointName} already exists'

    try:
        os.mkdir(ndir)
        #os.mkdir(os.path.join(ndir,'figures'))
        #os.mkdir(os.path.join(ndir,'stables')) 

    except:
        return False, f'Unable to create data files for {endpointName}'
    
    template = os.path.join (toxtrustPath(), 'endpoint.yaml') #'toxtrust', 'templates',

    try:    
        shutil.copy(template, ndir)
    except:
        return False, 'Unable to copy template file'
    
    e = Endpoint(endpointName)
    
    try:
        e.load()
    except:
        return False, f'Loading data for endpoint {endpointName} failed'

    e.setVal('id', generateId() )  # put in another place, 
    e.save()
    
    return True, f'Endpoint {endpointName} successfully created'

def removeEndpoint(endpointName):
    
    if not endpointName:
        return False, 'Empty endpoint name'
    
    ndir = endpointPath(endpointName)
    
    try:
        shutil.rmtree(ndir)
    except OSError as e:
        return False, f'Endpoint {endpointName} does not exist'
    
    return True, f'Endpoint {endpointName} successfully removed'

def listEndpoints():
    
    listEndpoints = os.listdir(endpointRepositoryPath())
    
    return listEndpoints
    
def generateId(size=10, chars=string.ascii_uppercase + string.digits):
    '''
    Return a random ID (used for temp files) with uppercase letters and numbers
    '''
    return ''.join(random.choice(chars) for _ in range(size))


