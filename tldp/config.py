#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging

from tldp.utils import logger, isdirectory, isloglevel
from tldp.cascadingconfig import CascadingConfig, DefaultFreeArgumentParser

import tldp.doctypes

status_types = ['all',
                'sources',
                'outputs',
                'new',
                'broken',
                'orphaned',
                'published',
                'stale',
                ]

def collectconfiguration(argv):
    tag = 'ldptool'
    argparser = DefaultFreeArgumentParser()
    argparser.add_argument('--build',
                           '-b',
                           nargs='*', default=None, type=str,
                           help='build LDP documentation')
    argparser.add_argument('--list',
                           '-l',
                           nargs='?', default=None, type=str,
                           choices=status_types,
                           help='list elements of LDP publication system')
    argparser.add_argument('--status',
                           '-t',
                           action='store_true', default=False,
                           help='produce a detailed status report of documents')
    argparser.add_argument('--all', 
                           '-a',
                           action='store_true', default=False,
                           help='process all documents (list, build or status)')
    argparser.add_argument('--loglevel', 
                           '-L',
                           default=logging.ERROR, type=isloglevel,
                           help='set the loglevel')
    argparser.add_argument('--sourcedir', '--source-dir', '--source-directory',
                           '-i',
                           action='append', default=None, type=isdirectory,
                           help='a directory containing LDP source documents')
    argparser.add_argument('--pubdir', '--output', '--outputdir', '--outdir',
                           '-o',
                           default=None, type=isdirectory,
                           help='a directory containing LDP output documents')
    argparser.add_argument('--configfile', '--config-file', '--cfg',
                           '-c',
                           default=None, type=isdirectory,
                           help='a configuration file')

    # -- collect up the fragments of CLI; automate detection?
    #
    tldp.doctypes.linuxdoc.config_fragment(argparser)
    tldp.doctypes.docbooksgml.config_fragment(argparser)
    tldp.doctypes.docbook4xml.config_fragment(argparser)
    tldp.doctypes.docbook5xml.config_fragment(argparser)

    cc = CascadingConfig(tag, argparser, argv)
    config, args = cc.parse()
    return config


def main(argv):
    config = collectconfiguration(argv)
    import pprint
    pprint.pprint(vars(config))
    return 0

#
# -- end of file
