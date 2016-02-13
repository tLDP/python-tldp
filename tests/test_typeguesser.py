
from __future__ import absolute_import, division, print_function

import os
import unittest
from tempfile import NamedTemporaryFile as ntf

# -- Test Data
from examples import *

# -- SUT
from tldp.typeguesser import guess


def genericGuessTest(content, ext):
        f = ntf(prefix='tldp-guesser-test-', suffix=ext, delete=False)
        f.write(content)
        f.flush()
        dt = guess(f.name)
        f.close()
        os.unlink(f.name)
        return dt


class TestDoctypes(unittest.TestCase):

    def testDetectionBySignature(self):
        for example in (ex_linuxdoc, ex_docbooksgml, ex_docbook4xml, 
                        ex_docbook5xml):
            dt = genericGuessTest(example['content'], example['ext'])
            self.assertEqual(example['type'], dt)

    def testDetectionByExtension(self):
        for example in (ex_rst, ex_markdown, ex_text):
            dt = genericGuessTest(example['content'], example['ext'])
            self.assertEqual(example['type'], dt)

    def testDetectionBogusExtension(self):
        dt = genericGuessTest('franks-cheese-shop', '.wmix')
        self.assertIsNone(dt)

    def testDetectionMissingExtension(self):
        dt = genericGuessTest('franks-cheese-shop', '')
        self.assertIsNone(dt)

    def testGuessNumber(self):
        self.assertIsNone(guess(7))

    def testGuessBadXML(self):
        dt = genericGuessTest('<valid class="bogus">XML</valid>', '.xml')
        self.assertIsNone(dt)

    def testGuessTooManyMatches(self):
        a = ex_docbook4xml['content']
        b = ex_docbook5xml['content'] 
        four, fourdt = a + b, ex_docbook4xml['type']
        dt = genericGuessTest(four, '.xml')
        self.assertIs(dt, fourdt)
        five, fivedt = b + a, ex_docbook5xml['type']
        dt = genericGuessTest(five, '.xml')
        self.assertIs(dt, fivedt)

#
# -- end of file
