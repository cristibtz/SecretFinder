from setuptools import setup

setup(
    name='secret-finder',
    version='0.0.1',
    description='Secret Finder Tool',
    author='Cristian Branet',
    author_email='branet.cristian@gmail.com',
    packages=['secret_finder'],
    entry_points={
        'console_scripts': [ 'secret-finder=secret_finder.main:main' ]
    }
)