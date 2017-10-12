try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

#from kdnb import __version__

config = {
    'description': 'Quickly SSH into a Netbox device..',
    'author': 'Jon Purdy',
    'url': 'https://github.com/jonpurdy/nbssh/',
    'author_email': 'jon+nbssh@jonpurdy.com',
    'version': 0.3,
    'install_requires': [
    'requests',
    'docopt',
    'inquirer',
    'blessings'
    ],
    'packages': ['nbssh'],
    'scripts': [],
    'license': 'GNU General Public License v3 (GPLv3)',
    'entry_points': {'console_scripts': ['nbssh=nbssh.__main__:main']},
    'name': 'nbssh'
}

setup(**config)
