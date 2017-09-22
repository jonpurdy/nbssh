from nose.tools import *
from nbssh.config_loader import load_config

try:
    config = load_config()
except AttributeError as e:
    print(e)
    print("Does the file have the correct format?")

def setup():
    print("SETUP!")


def test_teardown():
    print("TEAR DOWN!")

def test_basic():
    print("I RAN!")
