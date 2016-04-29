#! /usr/bin/python
# -*- coding: utf8 -*-
#
# Copyright (c) 2016 Linux Documentation Project

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import os
import sys

from argparse import ArgumentParser, ArgumentError, Namespace
from argparse import _UNRECOGNIZED_ARGS_ATTR

import logging
logger = logging.getLogger(__name__)

ENVSEP = NSSEP = '_'    # -- underscore _
CLISEP = CFGSEP = '-'   # -- dash -
MULTIVALUESEP = ','

try:
    from configparser import ConfigParser as ConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser as ConfigParser


def dict_to_argv_longform(d):
    '''creates from a dictionary, an invocation parseable by argparse

    :param: d, should be a dictionary

    Returns: a list that is suitable for passing to the method parser() on
             an argparse.ArgumentParser; basically, a list of whitespace-
             separated CLI options.

    This function produces a list that looks like sys.argv on the
    command-line.
    '''
    args = list()
    for opt, arg in d.items():
        if isinstance(arg, (tuple, list)):
            for x in arg:
                args.extend(("--" + opt, x))
        else:
            args.extend(("--" + opt, arg))
    return args


def empty2none_values(d):
    '''creates None values for values holding the empty string ("")

    :param: d, a dictionary
    '''
    for k, v in d.items():
        if v == '':
            d[k] = None
    return d


def convert_multivalues(d, multivaluesep=MULTIVALUESEP):
    '''creates multivalued values in an argument dict()

    :param: d, a dictionary
    :param: separator; optional, desired string separator

    Returns: a dictionary where any values containing the separator
             are now converted to lists, broken on the separator.

    This function assumes all keys are plain text.  It will adjust the content
    of any value which contains separator, by splitting on that separator and
    removing any whitespace around the resulting text elements.
    '''
    for k, v in d.items():
        if multivaluesep in v:
            d[k] = [x.strip() for x in v.split(multivaluesep)]
    return d


def dict_from_cfg(f, base=None, cfgsep=CFGSEP, clisep=CLISEP):
    '''read a configuration file, normalizing fields to CLI-parseable form

    :param: f, a filename or file-like object (readable via
            ConfigParser.read() [filename] or ConfigParser.fp() [open file]

    Returns: a dictionary where keys are section-field = value

    Will read a single configuration file into dict.  Each section of the
    configuration file is read and a dictionary is constructed by
    concatenating the section name and the field name to produce the key.

    It also normalizes all section names and fields (keys) to lowercase.
    This aids in comparisons in downstream processing where interacting with
    argparse and variables extracted from the environment.

    Given only:

      [frobnitz]
      pubdir = /path/to/a/publication/directory

    When invoked as:

      dict_from_cfg(f)  # -- where f is the pathname or open filehandle

    This function will return a dict that looks like this:

      {'frobnitz.pubdir': '/path/to/a/publication/directory'}
    '''
    d = dict()
    parser = ConfigParser()

    if isinstance(f, (list, tuple)) or os.path.isfile(f):
        parser.read(f)
    else:
        parser.readfp(f)

    for section in parser.sections():
        if base is not None:
            if not section.startswith(base):
                logger.debug("Skipping sect [%s] in %s (not prefixed with %s)",
                             section, f, base)
                continue
        sectname = section.lower().replace(cfgsep, clisep)
        for name, value in parser.items(section):
            keyname = name.lower().replace(cfgsep, clisep)
            d[clisep.join((sectname, keyname))] = value
    return d


def dict_from_envdict(env=os.environ, base=None, envsep=ENVSEP, clisep=CLISEP):
    '''read environment, normalizing all keys starting with 'base' to CLI form

    :param: env, if nothing is supplied, os.environ
    :param: base [optional], envar prefix filter selection criterion

    Returns:  a dictionary of the adjusted environment-variable name
              as the key and the value of the envar

    This function reads the environment (well, OK, any dictionary) and
    returns each entry that begins with base (plus underscore).

    It also normalizes all environment value names names (envars) to
    lowercase, since environments most often use uppercase names.  This aids
    in comparisons in downstream processing where interacting with argparse
    and variables extracted from configuration files.

    Given an environment:

      SSH_AGENT_PID=4753
      SSH_AUTH_SOCK=/tmp/ssh-2w3uWI19OqvG/agent.2638
      FROBNITZ=Waffle

    When invoked as:

      dict_from_envdict(os.environ, 'SSH')

    This function will return a dict that looks like this:

      {'ssh-agent-pid': '4753',
       'ssh-auth-sock': '/tmp/ssh-2w3uWI19OqvG/agent.2638'}

    When invoked as:

      dict_from_envdict(os.environ)

    This function will return a dict that looks like this:

      {'frobnitz': 'Waffle',
       'ssh-agent-pid': '4753',
       'ssh-auth-sock': '/tmp/ssh-2w3uWI19OqvG/agent.2638'}
    '''
    d = dict()
    if base is None:
        tag = ''
    else:
        tag = base + envsep
    for k, v in env.items():
        if k.startswith(tag):
            k = k.lower().replace(envsep, clisep)
            d[k] = str(v)
    return d


def prepend_tag(base, d, sep=CLISEP):
    newd = dict()
    tag = ''.join((base, sep))
    for k, v in d.items():
        newd[''.join((tag, k))] = v
    return newd


def strip_tag(base, d, clisep=CLISEP):
    if not base:
        return d
    newd = dict()
    tag = base + clisep
    for oldk, v in d.items():
        if oldk.startswith(tag):
            newk = oldk[len(tag):]
            if newk in newd:
                logger.debug("Duplicate key found when stripping %s from %s.",
                             tag, oldk)
                logger.info("strip_tag: returning unchanged dict().")
                return d
            newd[newk] = v
        else:
            newd[oldk] = v
    return newd


def dict_from_ns(ns):
    return vars(ns)


def ns_from_dict(d):
    ns = Namespace()
    for k, v in d.items():
        setattr(ns, k, v)
    return ns


def envdict_from_ns(tag, ns):
    d = dict_from_ns(ns)
    d = prepend_tag(tag, d, sep=ENVSEP)
    d = dict([(k.upper(), v) for k, v in d.items()])
    for k, v in sorted(d.items()):
        if v is None:
            d[k] = ''
        if isinstance(v, (list, tuple)):
            v = MULTIVALUESEP.join([str(x) for x in v])
            d[k] = v
    return d


def clilist_from_ns(ns):
    cli = list()
    d = dict_from_ns(ns)
    for k, v in sorted(d.items()):
        k = ''.join(('--', k.replace(NSSEP, CLISEP)))
        if isinstance(v, (list, tuple)):
            for val in v:
                cli.extend((k, str(val)))
        else:
            cli.extend((k, str(v)))
    return cli


def argv_from_env(args, tag, **kw):
    '''read a config file and produce argparse-compatible invocation

    :param:  args, a dictionary containing the environment (os.environ)
    :param:  tag, a prefix to remove from all config file field names
    :kw:  a prefix to remove from all field names read from the config file

    Returns an argparse-compatible list that looks like argv from a
    command-line.

    Given an environment dict:

      args = {
        'LDPTOOL_VERBOSE': '3',
        'LDPTOOL_SOURCEDIR': '/path/faq/docbook/,/path/howto/linuxdoc/'}

    When invoked as:

      argv_from_env(args, 'ldptool')

    This function will return a list that looks like this:

      ['--verbose', '3',
       '--sourcedir', '/path/faq/docbook/',
       '--sourcedir', '/path/howto/linuxdoc/']
    '''
    d = dict_from_envdict(args, base=tag.upper(), **kw)
    listify_values = kw.get('convert_multivalues', convert_multivalues)
    if listify_values is not None:
        d = listify_values(d)
    fix_empty = kw.get('empty2none_values', empty2none_values)
    if fix_empty is not None:
        d = fix_empty(d, **kw)
    d = strip_tag(tag, d)
    d = dict_to_argv_longform(d)
    return d


def argv_from_cfg(args, tag, **kw):
    '''read a config file and produce argparse-compatible invocation

    :param:  args, anything suitable to ConfigParser.read() [see note]
    :param:  tag, a prefix to remove from all config file field names

    Returns an argparse-compatible list that looks like argv from a
    command-line.

    Given a config file:

      [main]
      silly = 3

      [ldptool]
      sourcedir = /home/mabrown/vcs/LDP/LDP/howto/linuxdoc/,
                  /home/mabrown/vcs/LDP/LDP/howto/docbook/

      [ldptool.linuxdoc]
      sgml2html = /usr/bin/sgml2html

      [ldptool-docbook]
      xsltproc = /usr/bin/xsltproc

    When invoked as:

      argv_from_cfg(filename, 'ldptool')

    This function will return a list that looks like this:

      ['--sourcedir', '/home/mabrown/vcs/LDP/LDP/howto/linuxdoc/',
       '--sourcedir', '/home/mabrown/vcs/LDP/LDP/howto/docbook/',
       '--linuxdoc-sgml2html', '/usr/bin/sgml2html',
       '--docbook-xsltproc', '/usr/bin/xsltproc']
    '''
    d = dict_from_cfg(args, base=tag, **kw)
    listify_values = kw.get('convert_multivalues', convert_multivalues)
    if listify_values is not None:
        d = listify_values(d, **kw)
    fix_empty = kw.get('empty2none_values', empty2none_values)
    if fix_empty is not None:
        d = fix_empty(d, **kw)
    d = strip_tag(tag, d, **kw)
    d = dict_to_argv_longform(d, **kw)
    return d


class DefaultFreeArgumentParser(ArgumentParser):
    '''subclass of stock argparse.ArgumentParser; suppress default generation

    The vast majority of argparse users (and usage cases) would like to
    produce all defaults whenever parsing args/options.

    In this case, we would like to take configuration data from multiple
    sources and merge them.  It is important to omit any configured defaults
    so that it's clear where a configuration option came from.

    See the method parse_known_args_no_defaults().
    '''
    def parse_known_args_no_defaults(self, args=None, namespace=None):
        '''This method is the parse_known_args() method from the stock
        library, sans the block which sets the defaults in the Namespace().

        This method is called many times by CascadingConfig():

          - when processing CLI, returns only options found in user's CLI
          - when processing system configuration, returns only ...
          - when processing user configuration, returns only ...
          - when processing environment, returns only ...

        See also CascadingConfig()
        '''
        if args is None:
            # args default to the system args
            args = sys.argv[1:]
        else:
            # make sure that args are mutable
            args = list(args)

        # default Namespace built from parser defaults
        if namespace is None:
            namespace = Namespace()

        # parse the arguments and exit if there are any errors
        try:
            namespace, args = self._parse_known_args(args, namespace)
            if hasattr(namespace, _UNRECOGNIZED_ARGS_ATTR):
                args.extend(getattr(namespace, _UNRECOGNIZED_ARGS_ATTR))
                delattr(namespace, _UNRECOGNIZED_ARGS_ATTR)
            return namespace, args
        except ArgumentError:
            err = sys.exc_info()[1]
            self.error(str(err))


class CascadingConfig(object):
    '''container for all conf data read from environ, CLI and config files

    This class delegates most of the heavy lifting and processing of option
    processing to argparse, which is eminently suited to the rich set of
    possibilities, including type conversion and other user-defined
    data-dependent arbitrary checks.

    The CascadingConfig gathers configuration data from the following sources:

      - cli:  command-line options, supplied by the user
      - environment:  process environment
      - userconfig:  user-specific configuration file
      - systemconfig:  system-wide configuration file options
      - defaults:  defaults from parser (subclass of argparse.ArgumentParser)

    The resulting configuration is derived by applying rules of precedence for
    the configuration sources.  The order of precedence resolution is
    configurable.  The stock CascadingConfiguration resolution order is as
    follows:

      - cli            (highest precedence)
      - environment
      - userconfig
      - systemconfig
      - defaults       (lowest precedence)

    The order of resolution of configurations can be controlled by passing
    a list of sources to the set_config() method.  Here's the standard
    resolution order:

    order = ['cli', 'environment', 'userconfig', 'systemconfig', 'defaults']
    '''
    order = ['cli', 'environment', 'userconfig', 'systemconfig', 'defaults']
    mine = ['--dump_cli', '--dump_env', '--dump_cfg', '--debug_options']

    def __init__(self, tag, argparser, argv=sys.argv[1:], env=os.environ,
                 configfile='configfile', order=order):
        '''construct a CascadingConfig

        :param: tag, the config file prefix and envar prefix
        :param: parser, a DefaultFreeArgumentParser with all args set

        Optional:

        :param: argv, CLI args to use instead of sys.argv[1:]
        :param: env, environment dictionary to use instead of os.environ()
        :param: configfile, CLI name to use instead of 'configfile' to
                find the name(s) of the system and user configuration files
        :param: order, the precedence or resolution order of the various
                configuration sources

        The parser must not merge or supply defaults when returning a
        Namespace.  If it does that, then downstream consumers will not be
        able to handle precedence resolution themselves.
        '''
        # -- a wee-bit hackish; but this is crucial to the proper functioning
        #    of CascadingConfig
        #
        assert hasattr(argparser, 'parse_known_args_no_defaults')
        for opt in self.mine:
            synonym = opt.replace(NSSEP, CLISEP)
            argparser.add_argument(opt, synonym, action='store_true')

        # -- remember some attributes
        self.tag = tag
        self.argparser = argparser
        self.argv = argv
        self.env = env
        self.configfile = configfile
        self.order = order

    def parse(self):
        self.read_defaults()
        self.read_cli()
        self.read_environment()
        self.read_systemconfig()
        self.read_userconfig()
        self.set_config()
        self.handle_ccrequest()
        return self.config, self.cli_extras

    def read_defaults(self):
        '''read the defaults that the developer set in the ArgumentParser'''
        self.defaults = self.argparser.parse_args([])

    def read_cli(self):
        '''read configuration supplied by CLI (argv from constructor)'''
        parser = self.argparser.parse_known_args_no_defaults
        self.cli, self.cli_extras = parser(self.argv)

    def read_environment(self):
        '''read relevant environment variables'''
        parser = self.argparser.parse_known_args_no_defaults
        self.environment, extras = parser(argv_from_env(self.env, self.tag))
        self.environment_extras = extras

    def read_systemconfig(self):
        '''read the specified system configuration file'''
        parser = self.argparser.parse_known_args_no_defaults
        syscfg = getattr(self.defaults, self.configfile, None)
        self.syscfg = syscfg
        if syscfg is not None:
            self.systemconfig, extras = parser(argv_from_cfg(syscfg, self.tag))
            self.systemconfig_extras = extras
        else:
            self.systemconfig = Namespace()
            self.systemconfig_extras = list()

    def read_userconfig(self):
        '''read a single user specified configuration file'''
        parser = self.argparser.parse_known_args_no_defaults
        maybe = list()
        maybe.append(('cli', getattr(self.cli, self.configfile, None)))
        maybe.append(('env', getattr(self.environment, self.configfile, None)))
        for source, usrcfg in maybe:
            if usrcfg is None:
                continue
            elif usrcfg == self.syscfg:
                logger.info("Skipping systemconfig file %s in userconfig (%s)",
                            self.syscfg, source)
                continue
            else:
                logger.debug("Using %s for user config", usrcfg)
                break
        del maybe
        if usrcfg is None:
            self.userconfig = Namespace()
            self.userconfig_extras = list()
        else:
            logger.debug("Reading %s for user config", usrcfg)
            self.userconfig, extras = parser(argv_from_cfg(usrcfg, self.tag))
            self.userconfig_extras = extras

    def set_config(self, order=None):
        if order is not None:
            logger.debug("Installing custom resolution order %r", order)
        else:
            order = self.order
        sources = [(x, getattr(self, x)) for x in order]
        sources.reverse()
        config = Namespace()
        for sourcename, source in sources:
            for name in vars(source):
                newval = getattr(source, name)
                logger.debug("Source %s: %s=%s", sourcename, name, newval)
                oldval = getattr(config, name, None)
                if oldval is not None:
                    logger.debug("Source %s: replacing %s=%s with %s=%s",
                                 sourcename, name, oldval, name, newval)
                setattr(config, name, newval)
        self.config = config

    def dump_env(self):
        d = envdict_from_ns(self.tag, self.config)
        for k, v in sorted(d.items()):
            print('{}={}'.format(k, v))
        return 0

    def dump_cfg(self):
        d = dict_from_ns(self.config)
        d = prepend_tag(self.tag, d, sep=CFGSEP)
        cfg = ConfigParser()
        for k, v in d.items():
            k = k.replace(NSSEP, CFGSEP)
            parts = k.split(CFGSEP)
            assert len(parts) >= 2
            if 2 == len(parts):
                sect, field = parts[0], CFGSEP.join(parts[1:])
            else:
                sect = CFGSEP.join(parts[0:2])
                field = CFGSEP.join(parts[2:])
            if not cfg.has_section(sect):
                cfg.add_section(sect)
            if v is None:
                v = ''
            if isinstance(v, (list, tuple)):
                vstr = ',\n'.join([str(x) for x in v])
                cfg.set(sect, field, vstr)
            else:
                cfg.set(sect, field, str(v))
        cfg.write(sys.stdout)
        return 0

    def dump_cli(self):
        cli = clilist_from_ns(self.config)
        print(' '.join(cli))
        return 0

    def debug_options(self):
        import pprint
        for k, v in vars(self).items():
            if isinstance(v, Namespace):
                print('\n'.join(('', k, '----------')))
                pprint.pprint(vars(v))
            else:
                print('\n'.join(('', k, '----------')))
                pprint.pprint(v)
        return 0

    def handle_ccrequest(self):
        diagfunc = False
        for opt in self.mine:
            opt = opt.lstrip(CLISEP)
            if getattr(self.config, opt, False):
                diagfunc = getattr(self, opt)
            delattr(self.config, opt)
        if diagfunc:
                sys.exit(diagfunc())

#
# -- end of file
