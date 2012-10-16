'''
Created on 14-10-2012

@author: jurek
'''
import os
from setuptools import setup
from setuptools import find_packages
#from distutils.core import setup

application_name = os.environ["APPLICATION_NAME"]
application_description = os.environ["APPLICATION_DESCRIPTION"]
required_packages = os.environ["REQUIRED_PACKAGES"]
if (not (required_packages == None or len(required_packages) == 0
    or required_packages == '${required.packages}')):
    required_packages = required_packages.split(',')
else:
    required_packages = None

setup(
    name=application_name,
    version='0.1',
    description=application_description,
    author='Jerzy Ellert',
    author_email='jeel@epoczta.pl',
    #url='http://wiki.secondlife.com/wiki/Eventlet',
    packages=find_packages('src'),  # include all packages under src
    package_dir={'': 'src'},  # tell distutils packages are under src
    long_description=application_description,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Development Status :: Alpha-1",
        "Intended Audience :: Developers",
        "Topic :: Medical science",
    ],
    keywords='med',
    license='GPL',
    install_requires=required_packages,
)
