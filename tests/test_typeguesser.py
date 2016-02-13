
from __future__ import absolute_import, division, print_function

import os
import unittest
from tempfile import NamedTemporaryFile as ntf

# -- Test Data
import examples

# -- SUT
from tldp.typeguesser import guess
from tldp.doctypes.common import SignatureChecker


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
        for ex in examples.examples:
            if isinstance(ex.type, SignatureChecker):
                dt = genericGuessTest(ex.content, ex['ext'])
                self.assertEqual(ex.type, dt)

    def testDetectionByExtension(self):
        for ex in examples.examples:
            if not isinstance(ex.type, SignatureChecker):
                dt = genericGuessTest(ex.content, ex.ext)
                self.assertEqual(ex.type, dt)

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
        a = examples.ex_docbook4xml.content
        b = examples.ex_docbook5xml.content
        four, fourdt = a + b, examples.ex_docbook4xml.type
        dt = genericGuessTest(four, '.xml')
        self.assertIs(dt, fourdt)
        five, fivedt = b + a, examples.ex_docbook5xml.type
        dt = genericGuessTest(five, '.xml')
        self.assertIs(dt, fivedt)

#
# -- end of file
