#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging

from tldp.utils import logger, isdirectory, isloglevel
from tldp.cascadingconfig import CascadingConfig, DefaultFreeArgumentParser

import tldp.doctypes
from tldp.inventory import status_types


def collectconfiguration(tag, argv):
    argparser = DefaultFreeArgumentParser()
    argparser.add_argument('--build',
                           '-b',
                           nargs='*', default=None, type=str,
                           help='build LDP documentation')
    argparser.add_argument('--detail', '--list',
                           '-l',
                           default=None, type=str,
                           choices=tldp.inventory.status_types,
                           help='list elements of LDP publication system')
    argparser.add_argument('--status', '--summary',
                           '-t',
                           action='store_true', default=False,
                           help='produce a status report of the inventory')
    argparser.add_argument('--verbose', 
                           '-v',
                           action='store_true', default=False,
                           help='increase information produced during --list')
    argparser.add_argument('--loglevel', 
                           '-L',
                           default=logging.ERROR, type=isloglevel,
                           help='set the loglevel')
    argparser.add_argument('--sourcedir', '--source-dir', '--source-directory',
                           '-s',
                           action='append', default='', type=isdirectory,
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
    config = collectconfiguration('ldptool', argv)
    import pprint
    pprint.pprint(vars(config))
    return 0

#
# -- end of file
