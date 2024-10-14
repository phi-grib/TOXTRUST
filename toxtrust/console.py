#! -*- coding: utf-8 -*-

# Description    NAMASTOX command
#
# Authors:       Manuel Pastor (manuel.pastor@upf.edu)
#
# Copyright 2022 Manuel Pastor
#
# This file is part of NAMASTOX
#
# NAMASTOX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.
#
# Flame is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NAMASTOX. If not, see <http://www.gnu.org/licenses/>.

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