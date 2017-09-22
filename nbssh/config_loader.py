#!/usr/bin/env python

import os
import configparser


def load_config(config_location):
    '''
    Loads config from config.
    '''

    # Getting configuration first
    file_path = os.path.expanduser(config_location)
    # configparser silently fails if the file doesn't exist
    if os.path.isfile(file_path):
        config = configparser.ConfigParser()
        try:
            config.read(file_path)
        except Exception as e:
            print(e)
            print("Couldn't read configuration file.")
    else:
        print("Couldn't open config file. Has it been created as %s ?"
              % config_location)
        return 0

    return config
