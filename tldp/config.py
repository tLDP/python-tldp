#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import logging

from tldp.utils import arg_isdirectory, arg_isloglevel, arg_isreadablefile
from tldp.cascadingconfig import CascadingConfig, DefaultFreeArgumentParser

import tldp.typeguesser

logger = logging.getLogger(__name__)

DEFAULT_CONFIGFILE = '/etc/ldptool/ldptool.ini'


def collectconfiguration(tag, argv):
    ap = DefaultFreeArgumentParser()

    g = ap.add_mutually_exclusive_group()
    g.add_argument('--build',
                   '-b',
                   action='store_true', default=False,
                   help='build LDP documentation [%(default)s]')
    g.add_argument('--publish',
                   '-p',
                   action='store_true', default=False,
                   help='build and publish LDP documentation [%(default)s]')
    g.add_argument('--script',
                   '-S',
                   action='store_true', default=False,
                   help='dump runnable script [%(default)s]')
    g.add_argument('--detail', '--list',
                   '-l',
                   action='store_true', default=False,
                   help='list elements of LDP system [%(default)s]')
    g.add_argument('--summary',
                   '-t',
                   action='store_true', default=False,
                   help='dump inventory summary report [%(default)s]')
    g.add_argument('--doctypes', '--formats', '--format',
                   '--list-doctypes', '--list-formats',
                   '-T',
                   action='store_true', default=False,
                   help='show supported doctypes [%(default)s]')
    g.add_argument('--statustypes', '--list-statustypes',
                   action='store_true', default=False,
                   help='show status types and classes [%(default)s]')

    ap.add_argument('--verbose',
                    action='store_true', default=False,
                    help='more info in --list/--detail [%(default)s]')
    ap.add_argument('--loglevel',
                    default=logging.ERROR, type=arg_isloglevel,
                    help='set the loglevel')
    ap.add_argument('--skip',
                    default=[], action='append', type=str,
                    help='skip this stem during processing')
    ap.add_argument('--resources',
                    default=['images', 'resources'], action='append', type=str,
                    help='subdirs to copy during build [%(default)s]')
    ap.add_argument('--sourcedir', '--source-dir', '--source-directory',
                    '-s',
                    action='append', default='', type=arg_isdirectory,
                    help='a directory containing LDP source documents')
    ap.add_argument('--pubdir', '--output', '--outputdir', '--outdir',
                    '-o',
                    default=None, type=arg_isdirectory,
                    help='a directory containing LDP output documents')
    ap.add_argument('--builddir', '--build-dir', '--build-directory',
                    '-d',
                    default=None, type=arg_isdirectory,
                    help='a scratch directory used for building')
    ap.add_argument('--configfile', '--config-file', '--cfg',
                    '-c',
                    default=DEFAULT_CONFIGFILE,
                    type=arg_isreadablefile,
                    help='a configuration file')

    # -- collect up the distributed configuration fragments
    #
    for cls in tldp.typeguesser.knowndoctypes:
        argparse_method = getattr(cls, 'argparse', None)
        if argparse_method:
            argparse_method(ap)

    cc = CascadingConfig(tag, ap, argv)
    config, args = cc.parse()
    return config, args

#
# -- end of file
