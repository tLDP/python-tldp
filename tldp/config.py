#! /usr/bin/python
# -*- coding: utf8 -*-
#
# Copyright (c) 2016 Linux Documentation Project

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import os
import argparse
import copy as _copy

import logging

from tldp.utils import arg_isloglevel, arg_isreadablefile
from tldp.cascadingconfig import CascadingConfig, DefaultFreeArgumentParser

import tldp.typeguesser

logger = logging.getLogger(__name__)

DEFAULT_CONFIGFILE = '/etc/ldptool/ldptool.ini'


class DirectoriesExist(argparse._AppendAction):

    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.isdir(values):
            message = "No such directory: %r for option %r, aborting..."
            message = message % (values, option_string)
            logger.critical(message)
            raise ValueError(message)
        items = _copy.copy(argparse._ensure_value(namespace, self.dest, []))
        items.append(values)
        setattr(namespace, self.dest, items)


class DirectoryExists(argparse._StoreAction):

    def __call__(self, parser, namespace, values, option_string=None):
        if not os.path.isdir(values):
            message = "No such directory: %r for option %r, aborting..."
            message = message % (values, option_string)
            logger.critical(message)
            raise ValueError(message)
        setattr(namespace, self.dest, values)


class StoreTrueOrNargBool(argparse._StoreAction):

    _boolean_states = {'1': True, 'yes': True, 'true': True, 'on': True,
                       '0': False, 'no': False, 'false': False, 'off': False}

    def __init__(self, *args, **kwargs):
        super(argparse._StoreAction, self).__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            setattr(namespace, self.dest, True)
        else:
            boolval = self._boolean_states.get(values.lower(), None)
            if boolval is None:
                message = "Non-boolean value: %r for option %r, aborting..."
                message = message % (values, option_string)
                logger.critical(message)
                raise ValueError(message)
            else:
                setattr(namespace, self.dest, boolval)


def collectconfiguration(tag, argv):
    '''main specification of command-line (and config file) shape'''

    ap = DefaultFreeArgumentParser()
    ap.add_argument('--sourcedir', '--source-dir', '--source-directory',
                    '-s',
                    default=[], action=DirectoriesExist,
                    help='a directory containing LDP source documents')

    ap.add_argument('--pubdir', '--output', '--outputdir', '--outdir',
                    '-o',
                    default=None, action=DirectoryExists,
                    help='a directory containing LDP output documents')

    ap.add_argument('--builddir', '--build-dir', '--build-directory',
                    '-d',
                    default=None, action=DirectoryExists,
                    help='a scratch directory used for building')

    ap.add_argument('--configfile', '--config-file', '--cfg',
                    '-c',
                    default=DEFAULT_CONFIGFILE,
                    type=arg_isreadablefile,
                    help='a configuration file')

    ap.add_argument('--loglevel',
                    default=logging.ERROR, type=arg_isloglevel,
                    help='set the loglevel')

    ap.add_argument('--verbose',
                    action=StoreTrueOrNargBool, nargs='?', default=False,
                    help='more info in --list/--detail [%(default)s]')

    ap.add_argument('--skip',
                    default=[], action='append', type=str,
                    help='skip this stem during processing')

    ap.add_argument('--resources',
                    default=['images', 'resources'], action='append', type=str,
                    help='subdirs to copy during build [%(default)s]')

    # -- and the distinct, mutually exclusive actions this script can perform
    #
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--publish',
                   '-p',
                   action='store_true', default=False,
                   help='build and publish LDP documentation [%(default)s]')

    g.add_argument('--build',
                   '-b',
                   action='store_true', default=False,
                   help='build LDP documentation [%(default)s]')

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
