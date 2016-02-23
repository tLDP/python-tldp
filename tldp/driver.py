#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import sys

from tldp.utils import logger

import tldp.config
import tldp.inventory


def detail(config):
    i = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
    output_order = ['broken', 'stale', 'orphan', 'new']
    assert set(output_order).issubset(tldp.inventory.status_types)
    for status in output_order:
        if config.detail in ('all', status):
            s = getattr(i, status, None)
            assert s is not None
            print_list(s, status, verbose=config.verbose)
    return 0


def print_list(s, status, verbose):
    width = dict()
    width['status'] = max([len(x) for x in tldp.inventory.status_types])
    width['stem'] = max([len(x) for x in s.keys()])
    for stem, doc in s.items():
        if doc.status != status:
            continue
        s = '{d.status:{w[status]}} {d.stem:{w[stem]}}'.format(d=doc, w=width)
        print(s)
        if verbose:
            if not hasattr(doc, 'newer'):
                continue
            for f in doc.newer:
                fname = os.path.join(doc.dirname, f)
                print('  newer file {}'.format(fname))
            if not hasattr(doc, 'output'):
                continue
            if not hasattr(doc.output, 'missing'):
                continue
            for f in doc.output.missing:
                print('  missing file {}'.format(f))
    return 0

def status(config):
    i = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
    width = max([len(x) for x in tldp.inventory.status_types])
    for status in tldp.inventory.status_types:
        if status == 'all':
            continue
        count = len(getattr(i, status, 0))
        s = '{0:{width}} {1:}'.format(status, count, width=width)
        print(s)
    return 0


def build(config):
    return 0


def run():
    tag = os.path.basename(sys.argv[0]).strip('.py')
    argv = sys.argv[1:]
    config = tldp.config.collectconfiguration(tag, argv)

    # -- first, and foremost, set requested logging level
    #
    logger.setLevel(config.loglevel)
    
    # -- check to see if the user wishes to --list things
    #    this function and friends is called 'detail', because
    #    Python reserves a special (fundamental) meaning for the word
    #    list; but for the end-user they are synonyms
    #
    if config.detail:
        sys.exit(detail(config))

    # -- check to see if the user wants --status output
    #
    if config.status:
        if config.pubdir is None:
            sys.exit("Option --pubdir required for --status.")
        if not config.sourcedir:
            sys.exit("Option --sourcedir required for --status.")
        sys.exit(status(config))

    # -- our primary action is to try to build
    if config.build is None:
        config.all = True
    sys.exit(build(config))
    

#
# -- end of file
