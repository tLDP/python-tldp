
from __future__ import absolute_import, division, print_function

import unittest
from argparse import Namespace

# -- SUT
from tldp.config import collectconfiguration


class TestConfigWorks(unittest.TestCase):

    def test_basic(self):
        config, args = collectconfiguration('tag', [])
        self.assertIsInstance(config, Namespace)
        self.assertIsInstance(args, list)

    def test_singleoptarg(self):
        config, args = collectconfiguration('tag', ['--pubdir', '.'])
        self.assertEqual(config.pubdir, '.')

#
# -- end of file
