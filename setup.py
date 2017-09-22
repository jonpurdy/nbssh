try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

#from kdnb import __version__

config = {
    'description': 'Quickly SSH into a Netbox device..',
    'author': 'Jon Purdy',
    'url': 'n/a',
    'download_url': 'n/a',
    'author_email': 'jon@jonpurdy.com',
    'version': 1,
    'install_requires': [
    'requests',
    'docopt'
    ],
    'packages': ['nbssh'],
    'scripts': [],
    'entry_points': {'console_scripts': ['nbssh=nbssh.__main__:main']},
    'name': 'nbssh'
}

setup(**config)
