
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import os
import codecs
import unittest
from tempfile import NamedTemporaryFile as ntf

# -- Test Data
import example

# -- SUT
from tldp.typeguesser import guess
from tldp.doctypes.common import SignatureChecker


def genericGuessTest(content, ext):
        tf = ntf(prefix='tldp-guesser-test-', suffix=ext, delete=False)
        tf.close()
        with codecs.open(tf.name, 'w', encoding='utf-8') as f:
            f.write(content)
        dt = guess(tf.name)
        os.unlink(tf.name)
        return dt


class TestDoctypes(unittest.TestCase):

    def testDetectionBySignature(self):
        for ex in example.sources:
            if isinstance(ex.doctype, SignatureChecker):
                dt = genericGuessTest(ex.content, ex['ext'])
                self.assertEqual(ex.doctype, dt)

    def testDetectionByExtension(self):
        for ex in example.sources:
            if not isinstance(ex.doctype, SignatureChecker):
                dt = genericGuessTest(ex.content, ex.ext)
                self.assertEqual(ex.doctype, dt)

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

    def testGuessSingleMatchAsciidoc(self):
        ex = example.ex_asciidoc
        dt = genericGuessTest(ex.content, '.txt')
        self.assertEqual(ex.doctype, dt)

    def testGuessTooManyMatches(self):
        a = example.ex_docbook4xml.content
        b = example.ex_docbook5xml.content
        four, fourdt = a + b, example.ex_docbook4xml.doctype
        dt = genericGuessTest(four, '.xml')
        self.assertIs(dt, fourdt)
        five, fivedt = b + a, example.ex_docbook5xml.doctype
        dt = genericGuessTest(five, '.xml')
        self.assertIs(dt, fivedt)

#
# -- end of file
