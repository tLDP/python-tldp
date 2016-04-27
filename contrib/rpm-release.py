#! /usr/bin/python
#
#

from __future__ import print_function

import os
import sys

from tldp import VERSION

fin = open(os.path.join(os.path.dirname(__file__), 'tldp.spec.in'))
fout = open(os.path.join(os.path.dirname(__file__), 'tldp.spec'))

def transform(mapping, text):
    for tag, replacement in mapping.iteritems():
        text = text.replace(tag, replacement)
    return text

subst = {'@' + VERSION + '@': VERSION}

fout.write(transform(subst, fin.read()))

# -- end of file
