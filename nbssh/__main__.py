#!/usr/bin/env python

"""Usage:
    nbssh [--debug](--refresh|QUERY)

Options:
    --debug        Log debug messages
    --refresh      Refresh the list of servers from Netbox
    --help         Print this help screen
"""

# Standard library
import sys
import logging
import subprocess
import os
import json
import time
from pprint import pprint

# 3rd party
import requests
import docopt
#import pick
import inquirer
from blessings import Terminal

# self
import config_loader

# parse docopt
arguments = docopt.docopt(__doc__, options_first=True)

if arguments['--debug']:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

# Set configuration and logging up first
config_location = "~/.nbssh"
config = config_loader.load_config(config_location)
if config == 0:
    sample_config = """Sample configuration:

[main]
API_ADDRESS = https://netbox.yourdomain.com
LOG_LOCATION = /var/log/nbssh.log
API_TOKEN = Token abc123
    """
    print(sample_config)
    sys.exit()

logging.basicConfig(level=log_level,
                    format='[%(asctime)s][%(levelname)s][%(name)s] \
                    %(message)s',
                    filename=config.get('main', 'LOG_LOCATION'))

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)


def main():
    query = arguments['QUERY']
    # file_location = "~/.nbssh-cache"
    # filename = os.path.expanduser("%s" % file_location)

    # if arguments['--refresh']:
    #     print("Refreshing from Netbox API...")
    #     all_devices = get_all_devices(config.get('main', 'API_ADDRESS'),
    #                                config.get('main', 'API_TOKEN'))
    #     save_devices_to_file(all_devices, filename)
    #     sys.exit()

    # all_devices = read_devices_from_file(filename)

    # i = 1
    # displayed_device_list_length = 20
    # devices = []
    # for device in all_devices:
    #     if i < displayed_device_list_length:
    #         if query in  device.name:
    #             devices.append(device)
    #             i += 1
    # if i >= displayed_device_list_length:
    #     print("Displaying the first %s results only. You might want to try a more specific search." % displayed_device_list_length)

    term = Terminal()

    displayed_device_list_length = 20
    devices = get_devices_by_query(config.get('main', 'API_ADDRESS'),
                                   config.get('main', 'API_TOKEN'),
                                   query,
                                   displayed_device_list_length)

    if len(devices) >= displayed_device_list_length:
        print("Displaying the first %s results only. You might want to try a more specific search." % displayed_device_list_length)
    # if there's a single result, just SSH directly without displaying the menu
    elif len(devices) == 1:
        print(term.bright_magenta("Single result. Going directly to %s..." % devices[0].name))
        os.system("ssh root@%s" % devices[0].primary_ip_address)
        sys.exit()
    elif len(devices) == 0:
        print("No results.")
        sys.exit()

    pick_options = []
    desired_length = 0
    for device in devices:
        if len(device.name) > desired_length:
            desired_length = len(device.name)
    for device in devices:
        #pick_options.append("%s  →  %s" % (make_string_this_length(device.name, 30), device.primary_ip_address))
        pick_options.append(make_string_this_length(device.name, desired_length))

    jon_theme = {"List": {
                    "selection_color": "black_on_cyan",
                    "selection_cursor": " ",
                    "unselected_color": "normal"
                    },
                 "Question": {
                    "mark_color": "white",
                    "brackets_color": "bright_magenta",
                    "default_color": "white_on_magenta",
                    }
                }

    questions = [inquirer.List('selection',
                                message="Which device?",
                                choices=pick_options,
                ),]
    answers = inquirer.prompt(questions, theme=inquirer.themes.load_theme_from_dict(jon_theme))
    if answers is None:
        exit()
    selection = answers['selection']

    for device in devices: 
        if device.name in selection:
            os.system("ssh root@%s" % device.primary_ip_address)

def get_all_devices(NB_API_ADDRESS, API_TOKEN):

    headers = {'Authorization': API_TOKEN,
               'Accept': 'application/json'}

    requests.packages.urllib3.disable_warnings()

    devices = []

    try:
        url = '%s/api/dcim/devices/?limit=1000' % NB_API_ADDRESS
        logger.debug(url)
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        logger.debug(e)

    for item in r.json()['results']:

        if item['primary_ip']:
            this_device = Device(device_id=item["id"],
                                 name=item["name"],
                                 primary_ip_address=item['primary_ip']['address'][:-3])
            devices.append(this_device)

    return devices

def get_devices_by_query(NB_API_ADDRESS, API_TOKEN, query, limit):
    """ Reads each server from the Netbox API, creates a Server object,
    """

    headers = {'Authorization': API_TOKEN,
               'Accept': 'application/json'}

    requests.packages.urllib3.disable_warnings()

    devices = []

    try:
        url = '%s/api/dcim/devices/?q=%s&limit=%s' % (NB_API_ADDRESS, query, limit)
        logger.debug(url)
        r = requests.get(url, headers=headers, verify=False)
    except Exception as e:
        logging.debug(e)

    i = 1
    # print(pprint(r.json()['results']))

    for item in r.json()['results']:

        if item['primary_ip']:
            this_device = Device(device_id=i,
                                 name=item["name"],
                                 primary_ip_address=item['primary_ip']['address'][:-3])
            devices.append(this_device)
            i += 1


    return devices

def save_devices_to_file(devices, filename):

    import pickle

    file_obj = open(filename,'wb+')

    try:
        pickle.dump(devices, file_obj)
    except Exception as e:
        print(e)
        exit()
    file_obj.close()

def read_devices_from_file(filename):

    import pickle

    if os.path.isfile(filename):
        try:
            file_obj = open(filename,'rb')
            devices = pickle.load(file_obj)
            return devices
        except Exception as e:
            print(e)
            print("Couldn't read configuration file.")
    else:
        print("Couldn't open file")

def make_string_this_length(input_string, desired_length):

    difference = desired_length - len(input_string)
    while difference > -1:
        input_string += " "
        difference -= 1
    return input_string

class Device(object):
    """ Server object.
    """

    device_id = 0
    selection_id = 0
    name = ""
    group_slug = ""
    primary_ip_address = ""
    authorized_keys = ""
    site = ""

    def __init__(self, device_id, name, primary_ip_address):
        self.device_id = device_id
        self.name = name
        self.primary_ip_address = primary_ip_address


if __name__ == '__main__':

    try:
        main()
    except (KeyboardInterrupt):
        print("Exiting...")
        logging.warn("Somebody hit Ctrl-C. Exiting.")
        sys.exit()
