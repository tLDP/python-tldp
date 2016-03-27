
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import unittest
import argparse
from argparse import Namespace

from tldptesttools import TestToolsFilesystem
from tldptesttools import CCTestTools

# -- SUT
from tldp.cascadingconfig import CascadingConfig
from tldp.cascadingconfig import DefaultFreeArgumentParser


class Test_argv_from_env(unittest.TestCase):

    def test_argv_from_env(self):
        pass


class Test_argv_from_cfg(TestToolsFilesystem):

    def setUp(self):
        self.makeTempdir()

    def tearDown(self):
        self.removeTempdir()

    def test_argv_from_env(self):
        pass


class TestDefaultFreeArgumentParser(unittest.TestCase):

    def test_basic(self):
        ap = DefaultFreeArgumentParser()
        self.assertIsInstance(ap, argparse.ArgumentParser)
        self.assertIsInstance(ap, DefaultFreeArgumentParser)


class TestCascadingConfig(unittest.TestCase):

    def setUp(self):
        self.ap = DefaultFreeArgumentParser()

    def test_constructor(self):
        cc = CascadingConfig('tag', self.ap, [])
        self.assertIsInstance(cc, CascadingConfig)

    def test_parse(self):
        cc = CascadingConfig('tag', self.ap, [])
        config, args = cc.parse()
        self.assertIsInstance(config, Namespace)
        self.assertIsInstance(args, list)


class TestCascadingConfigBasic(TestToolsFilesystem):

    def setUp(self):
        self.makeTempdir()
        self.ap = DefaultFreeArgumentParser()
        self.ap.add_argument('--sneeze', action='store_true', default=False)
        self.ap.add_argument('--eructate', default=[], type=str)

    def test_reading_env(self):
        argv = []
        env = {'EFFLUVIA_SNEEZE': 'True'}
        cc = CascadingConfig('effluvia', self.ap, argv=argv, env=env)
        config, args = cc.parse()
        self.assertTrue(config.sneeze)


class CascadingConfigBasicTest(CCTestTools):

    def test_defaults_returned(self):
        ap = DefaultFreeArgumentParser()
        ap.add_argument('--configfile', default=None, type=str)
        ap.add_argument('--size', default=9, type=int)

        c = Namespace(
          tag='tag',
          argparser=ap,
          argv=''.split(),
          env=dict(),
          cfg='',
          exp_config=Namespace(size=9),
          exp_args=[],
        )

        cc = CascadingConfig(c.tag, c.argparser, argv=c.argv, env=c.env)
        config, args = cc.parse()
        self.assertEqual(c.exp_config.size, config.size)

    def test_cfg_is_read_passed_by_env(self):
        ap = DefaultFreeArgumentParser()
        ap.add_argument('--configfile', default=None, type=str)
        ap.add_argument('--size', default=9, type=int)

        c = Namespace(
          tag='tag',
          argparser=ap,
          argv=''.split(),
          env=dict(),
          cfg='[tag]\nsize = 8',
          exp_config=Namespace(size=8),
          exp_args=[],
        )

        self.writeconfig(c)
        c.env.setdefault('TAG_CONFIGFILE', c.configfile)
        cc = CascadingConfig(c.tag, c.argparser, argv=c.argv, env=c.env)
        config, args = cc.parse()
        self.assertEqual(c.exp_config.size, config.size)

    def test_cfg_is_read_passed_by_argv(self):
        ap = DefaultFreeArgumentParser()
        ap.add_argument('--configfile', default=None, type=str)
        ap.add_argument('--size', default=9, type=int)

        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        c = Namespace(
          tag='tag',
          argparser=ap,
          argv=''.split(),
          env=dict(),
          cfg='[tag]\nsize = 8',
          exp_config=Namespace(size=8),
          exp_args=[],
        )
        self.writeconfig(c)
        c.argv.extend(['--configfile', c.configfile])
        cc = CascadingConfig(c.tag, c.argparser, argv=c.argv, env=c.env)
        config, args = cc.parse()
        self.assertEqual(c.exp_config.size, config.size)

    def test_precedence_env_cfg(self):
        ap = DefaultFreeArgumentParser()
        ap.add_argument('--configfile', default=None, type=str)
        ap.add_argument('--size', default=9, type=int)

        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        c = Namespace(
          tag='tag',
          argparser=ap,
          argv=''.split(),
          env=dict(TAG_SIZE=7, ),
          cfg='[tag]\nsize = 8',
          exp_config=Namespace(size=7),
          exp_args=[],
        )
        self.writeconfig(c)
        c.argv.extend(['--configfile', c.configfile])
        cc = CascadingConfig(c.tag, c.argparser, argv=c.argv, env=c.env)
        config, args = cc.parse()
        self.assertEqual(c.exp_config.size, config.size)

    def test_precedence_argv_env_cfg(self):
        ap = DefaultFreeArgumentParser()
        ap.add_argument('--configfile', default=None, type=str)
        ap.add_argument('--size', default=9, type=int)

        import logging
        logging.getLogger().setLevel(logging.DEBUG)
        c = Namespace(
          tag='tag',
          argparser=ap,
          argv='--size 6'.split(),
          env=dict(TAG_SIZE=7, ),
          cfg='[tag]\nsize = 8',
          exp_config=Namespace(size=6),
          exp_args=[],
        )
        self.writeconfig(c)
        c.argv.extend(['--configfile', c.configfile])
        cc = CascadingConfig(c.tag, c.argparser, argv=c.argv, env=c.env)
        config, args = cc.parse()
        self.assertEqual(c.exp_config.size, config.size)

    def test_basic_emptydefault(self):
        ap = DefaultFreeArgumentParser()
        ap.add_argument('--source', default='', action='append', type=str)

        c = Namespace(
          tag='tag',
          argparser=ap,
          argv=''.split(),
          env=dict(),
          cfg='',
          exp_config=Namespace(source=''),
          exp_args=[],
        )
        cc = CascadingConfig(c.tag, c.argparser, argv=c.argv, env=c.env)
        config, args = cc.parse()
        self.assertEqual(c.exp_config, config)
        self.assertEqual(c.exp_args, args)

    def test_basic_argv(self):
        ap = DefaultFreeArgumentParser()
        ap.add_argument('--source', default='', action='append', type=str)

        c = Namespace(
          tag='tag',
          argparser=ap,
          argv='--source /some/path'.split(),
          env=dict(),
          cfg='',
          exp_config=Namespace(source=['/some/path']),
          exp_args=[],
        )
        cc = CascadingConfig(c.tag, c.argparser, argv=c.argv, env=c.env)
        config, args = cc.parse()
        self.assertEqual(c.exp_config, config)
        self.assertEqual(c.exp_args, args)

# -- end of file
