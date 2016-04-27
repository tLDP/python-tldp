# -*- coding: utf-8 -*-
import os

import glob
from setuptools import setup
from tldp import VERSION


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as r_file:
    readme = r_file.read()


setup(
    name='tldp',
    version=VERSION,
    license='MIT',
    author='Martin A. Brown',
    author_email='martin@linux-ip.net',
    url="http://en.tldp.org/",
    description='automatic publishing tool for DocBook, Linuxdoc and Asciidoc',
    long_description=readme,
    packages=['tldp', 'tldp/doctypes'],
    test_suite='nose.collector',
    install_requires=['networkx', 'nose'],
    include_package_data=True,
    package_data={'extras': ['extras/collateindex.pl'],
                  'extras/xsl': glob.glob('extras/xsl/*.xsl'),
                  'extras/css': glob.glob('extras/css/*.css'),
                  'extras/dsssl': glob.glob('extras/dsssl/*.dsl'),
                  },
    data_files=[('/etc/ldptool', ['etc/ldptool.ini']), ],
    entry_points={
        'console_scripts': ['ldptool = tldp.driver:main', ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
