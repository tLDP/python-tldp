#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import logging

from tldp.utils import logger, arg_isdirectory, arg_isloglevel
from tldp.cascadingconfig import CascadingConfig, DefaultFreeArgumentParser

import tldp.doctypes
from tldp.inventory import status_classes


def collectconfiguration(tag, argv):
    ap = DefaultFreeArgumentParser()
    ap.add_argument('--build',
                    '-b',
                    action='store_true', default=False,
                    help='build LDP documentation [%(default)s]')
    ap.add_argument('--detail', '--list',
                    '-l',
                    action='store_true', default=False,
                    help='list elements of LDP system [%(default)s]')
    ap.add_argument('--status', '--summary',
                    '-t',
                    action='store_true', default=False,
                    help='dump inventory status report [%(default)s]')
    ap.add_argument('--verbose',
                    action='store_true', default=False,
                    help='more info in --list and --status [%(default)s]')
    ap.add_argument('--loglevel',
                    '-L',
                    default=logging.ERROR, type=arg_isloglevel,
                    help='set the loglevel')
    ap.add_argument('--sourcedir', '--source-dir', '--source-directory',
                    '-s',
                    action='append', default='', type=arg_isdirectory,
                    help='a directory containing LDP source documents')
    ap.add_argument('--pubdir', '--output', '--outputdir', '--outdir',
                    '-o',
                    default=None, type=arg_isdirectory,
                    help='a directory containing LDP output documents')
    ap.add_argument('--configfile', '--config-file', '--cfg',
                    '-c',
                    default=None, type=arg_isdirectory,
                    help='a configuration file')

    # -- collect up the fragments of CLI; automate detection?
    #
    tldp.doctypes.linuxdoc.config_fragment(ap)
    tldp.doctypes.docbooksgml.config_fragment(ap)
    tldp.doctypes.docbook4xml.config_fragment(ap)
    tldp.doctypes.docbook5xml.config_fragment(ap)

    cc = CascadingConfig(tag, ap, argv)
    config, args = cc.parse()
    return config, args

#
# -- end of file
