'''
Created on 14-10-2012

@author: jurek
'''
import os
from setuptools import setup
from setuptools import find_packages
#from distutils.core import setup


def _split_parameter_value(name, alias):
    parameter = os.environ.get(name, None)
    if (not (parameter == None or len(parameter) == 0
              or parameter == alias)):
        return parameter.split(',')


application_name = os.environ["APPLICATION_NAME"]
application_description = os.environ["APPLICATION_DESCRIPTION"]
required_packages = _split_parameter_value("REQUIRED_PACKAGES",
                                           "${required.packages}")
additional_files = _split_parameter_value("ADDITIONAL_FILES",
                                          "${additional.files}")
package_data = {'': additional_files, } if additional_files else {}

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
    package_data=package_data,
)
