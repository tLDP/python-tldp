#! /usr/bin/python
#
#

from __future__ import print_function

import os
import sys

opd = os.path.dirname
opj = os.path.join

sys.path.insert(0, opd(opd(__file__)))
from tldp import VERSION

fin = open(opj(opd(__file__), 'tldp.spec.in'))
fout = open(opj(opd(__file__), 'tldp.spec'), 'w')

def transform(mapping, text):
    for tag, replacement in mapping.items():
        text = text.replace(tag, replacement)
    return text

subst = {'@VERSION@': VERSION}
print(subst)

fout.write(transform(subst, fin.read()))

# -- end of file
