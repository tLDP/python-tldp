
from __future__ import absolute_import, division, print_function

from tldptesttools import TestInventoryBase

# -- Test Data
import example

# -- SUT
import tldp.driver


class TestDriverBuild(TestInventoryBase):

    def test_build_one_broken(self):
        self.add_docbook4xml_xsl_to_config()
        c = self.config
        c.build = True
        self.add_new('Frobnitz-DocBook-XML-4-HOWTO', example.ex_docbook4xml)
        # -- mangle the content of a valid DocBook XML file
        borked = example.ex_docbook4xml.content[:-12]
        self.add_new('Frobnitz-Borked-XML-4-HOWTO',
                     example.ex_docbook4xml, content=borked)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(2, len(inv.all.keys()))
        docs = inv.all.values()
        result = tldp.driver.build(c, docs)
        self.assertTrue('Build failed' in result)

    def test_build_only_requested_stem(self):
        c = self.config
        ex = example.ex_linuxdoc
        self.add_published('Published-HOWTO', ex)
        self.add_new('New-HOWTO', ex)
        argv = ['--pubdir', c.pubdir, '--sourcedir', c.sourcedir[0]]
        argv.extend(['--build', 'Published-HOWTO'])
        tldp.driver.run(argv)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(1, len(inv.published.keys()))
        self.assertEquals(1, len(inv.work.keys()))


class TestDriverPublish(TestInventoryBase):

    def test_publish_docbook4xml(self):
        self.add_docbook4xml_xsl_to_config()
        c = self.config
        c.publish = True
        self.add_new('Frobnitz-DocBook-XML-4-HOWTO', example.ex_docbook4xml)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(1, len(inv.all.keys()))
        docs = inv.all.values()
        exitcode = tldp.driver.publish(c, docs)
        self.assertEquals(exitcode, 0)
        doc = docs.pop(0)
        self.assertTrue(doc.output.iscomplete)

    def test_publish_asciidoc(self):
        self.add_docbook4xml_xsl_to_config()
        c = self.config
        c.publish = True
        self.add_new('Frobnitz-Asciidoc-HOWTO', example.ex_asciidoc)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(1, len(inv.all.keys()))
        docs = inv.all.values()
        c.skip = []
        exitcode = tldp.driver.publish(c, docs)
        self.assertEquals(exitcode, 0)
        doc = docs.pop(0)
        self.assertTrue(doc.output.iscomplete)

    def test_publish_linuxdoc(self):
        c = self.config
        c.publish = True
        self.add_new('Frobnitz-Linuxdoc-HOWTO', example.ex_linuxdoc)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(1, len(inv.all.keys()))
        docs = inv.all.values()
        c.skip = []
        exitcode = tldp.driver.publish(c, docs)
        self.assertEquals(exitcode, 0)
        doc = docs.pop(0)
        self.assertTrue(doc.output.iscomplete)

    def test_publish_docbooksgml(self):
        self.add_docbooksgml_support_to_config()
        c = self.config
        c.publish = True
        self.add_new('Frobnitz-DocBookSGML-HOWTO', example.ex_docbooksgml)
        inv = tldp.inventory.Inventory(c.pubdir, c.sourcedir)
        self.assertEquals(1, len(inv.all.keys()))
        docs = inv.all.values()
        exitcode = tldp.driver.publish(c, docs)
        self.assertEquals(exitcode, 0)
        doc = docs.pop(0)
        self.assertTrue(doc.output.iscomplete)

#
# -- end of file
