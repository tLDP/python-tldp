
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals


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

    def test_nonexistent_directory(self):
        argv = ['--pubdir', '/path/to/nonexistent/directory']
        with self.assertRaises(ValueError) as ecm:
            config, args = collectconfiguration('tag', argv)
        e = ecm.exception
        self.assertTrue("/path/to/nonexistent/directory" in e.args[0])

#
# -- end of file
