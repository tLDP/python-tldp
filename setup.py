# -*- coding: utf-8 -*-
import os

from setuptools import setup, find_packages


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as r_file:
    readme = r_file.read()


setup(
    name='tldp',
    version='0.1',
    license='GNU',
    author='Martin A. Brown',
    author_email='martin@linux-ip.net',
    description='tools for processing all TLDP source documents',
    long_description=readme,
    packages=find_packages(),
    test_suite='tests',
    install_requires=[
        'six>=1.7',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
