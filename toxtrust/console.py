
# Licence disclaimer missing

import os
import argparse

from toxtrust.config import configure, endpointRepositoryPath, toxtrustPath

def main():

    parser = argparse.ArgumentParser(description='TOXTRUST')

    parser.add_argument("--configure", 
                        action="store_true",
                        help="Run the configuration process",
                        required=False)

    # Not used now, coz we don't want to mix it! 
    
    parser.add_argument("--data",
                        action="store_true",
                        help="Show the path to the endpoint repository")
    
    parser.add_argument("--repository",
                    action="store_true",
                    help="Show the path to the endpoint repository")
    

    args = parser.parse_args()
    
    # Call the configure function if the configure flag is set
    if args.configure:
        success, message = configure()
        if success:
            return True, message
            #LOG.info("Configuration successful: " + message)
        else:
            return False, message
            #LOG.error("Configuration failed: " + message)
    
    if args.repository:
        toxtrust_repository = toxtrustPath()
        return True, toxtrust_repository
    
    if args.data:
        endpoint_repository = endpointRepositoryPath()
        return True, endpoint_repository

if __name__ == '__main__':
    main()
    
2