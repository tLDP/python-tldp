#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import sys
import logging
logger = logging.getLogger()

import tldp

from argparse import Namespace


def detail(config, args):
    i = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
    width = Namespace()
    width.status = max([len(x) for x in tldp.inventory.status_types])
    width.stem = max([len(x) for x in i.source.keys()])
    for arg in args:
        status_class = tldp.inventory.status_classes[arg]
        for status in status_class:
            s = getattr(i, status, None)
            assert s is not None
            for stem, doc in s.items():
                # -- a 'stale' or 'broken' document is implicitly a 'published'
                #    document as well, but we only want to list each document
                #    once
                #
                if doc.status == status:
                    doc.detail(width, config.verbose, file=sys.stdout)
    return 0


def status(config, args):
    i = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
    width = Namespace()
    width.status = max([len(x) for x in tldp.inventory.status_types])
    width.count = len(str(len(i.source.keys())))
    for status in tldp.inventory.status_types:
        if status == 'all':
            continue
        count = len(getattr(i, status, 0))
        s = '{0:{w.status}}  {1:{w.count}}  '.format(status, count, w=width)
        print(s, end="")
        if config.verbose:
            print('\t'.join(getattr(i, status).keys()))
        else:
            abbrev = getattr(i, status).keys()
            displaynum = 3
            if len(abbrev) > displaynum:
                abbrev = abbrev[:displaynum]
                remainder = count - displaynum
                abbrev.append('[and %d more]' % (remainder,))
            print('\t'.join(abbrev))
    return 0


def build(config, args):
    targets = list()
    if not args:
        i = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
        targets.extend(i.new.values())
        targets.extend(i.stale.values())
        targets.extend(i.broken.values())
    else:
        for arg in args:
            if os.path.isfile(arg):
                source = tldp.sources.SourceDocument(arg)
                targets.append(source)
    for source in targets:
        if not source.output:
            dirname = os.path.join(config.pubdir, source.stem)
            source.output = tldp.outputs.OutputDirectory(dirname)
        if not source.doctype:
            logger.warning("%s skipping document of unknown doctype", 
                           source.stem)
            continue
        output = source.output
        runner = source.doctype(source=source, output=output, config=config)
        runner.generate()
    return 0


def run():
    tag = os.path.basename(sys.argv[0]).strip('.py')
    argv = sys.argv[1:]
    config, args = tldp.config.collectconfiguration(tag, argv)

    # -- first, and foremost, set requested logging level
    #
    #logger.setLevel(config.loglevel)

    # -- check to see if the user wishes to --list things
    #    this function and friends is called 'detail', because
    #    Python reserves a special (fundamental) meaning for the word
    #    list; but for the end-user they are synonyms
    #
    if config.detail:
        sys.exit(detail(config, args))

    # -- check to see if the user wants --status output
    #
    if config.status:
        if config.pubdir is None:
            sys.exit("Option --pubdir required for --status.")
        if not config.sourcedir:
            sys.exit("Option --sourcedir required for --status.")
        sys.exit(status(config, args))

    # -- our primary action is to try to build
    if config.build is None:
        config.all = True
    sys.exit(build(config, args))

#
# -- end of file
