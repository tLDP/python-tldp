
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import os
import codecs
import random
import shutil
import unittest
from tempfile import mkdtemp
from tempfile import NamedTemporaryFile as ntf

import tldp.config
from tldp.outputs import OutputNamingConvention
from tldp.utils import writemd5sums, md5file

# -- short names
#
opa = os.path.abspath
opb = os.path.basename
opd = os.path.dirname
opj = os.path.join

extras = opa(opj(opd(opd(__file__)), 'extras'))


def stem_and_ext(name):
    stem, ext = os.path.splitext(os.path.basename(name))
    assert ext != ''
    return stem, ext


def dir_to_components(reldir):
    reldir, basename = os.path.split(os.path.normpath(reldir))
    components = [basename]
    while reldir != '':
        reldir, basename = os.path.split(reldir)
        components.append(basename)
    assert len(components) >= 1
    components.reverse()
    return components


class TestToolsFilesystem(unittest.TestCase):

    def setUp(self):
        self.makeTempdir()

    def tearDown(self):
        self.removeTempdir()

    def makeTempdir(self):
        self.tempdir = mkdtemp(prefix='tldp-test-')

    def removeTempdir(self):
        shutil.rmtree(self.tempdir)

    def adddir(self, reldir):
        components = dir_to_components(reldir)
        absdir = self.tempdir
        while components:
            absdir = os.path.join(absdir, components.pop(0))
            if not os.path.isdir(absdir):
                os.mkdir(absdir)
        self.assertTrue(os.path.isdir(absdir))
        relpath = os.path.relpath(absdir, self.tempdir)
        return relpath, absdir

    def addfile(self, reldir, filename, stem=None, ext=None):
        dirname = os.path.join(self.tempdir, reldir)
        assert os.path.isdir(dirname)
        if stem is None:
            stem, _ = stem_and_ext(filename)
        if ext is None:
            _, ext = stem_and_ext(filename)
        newname = os.path.join(dirname, stem + ext)
        if os.path.isfile(filename):
            shutil.copy(filename, newname)
        else:
            with open(newname, 'w'):
                pass
        relname = os.path.relpath(newname, self.tempdir)
        return relname, newname


class CCTestTools(unittest.TestCase):

    def setUp(self):
        self.makeTempdir()

    def tearDown(self):
        self.removeTempdir()

    def makeTempdir(self):
        self.tempdir = mkdtemp(prefix='tldp-test-')

    def removeTempdir(self):
        shutil.rmtree(self.tempdir)

    def writeconfig(self, case):
        tf = ntf(prefix=case.tag, suffix='.cfg', dir=self.tempdir, delete=False)
        tf.close()
        with codecs.open(tf.name, 'w', encoding='utf-8') as f:
            f.write(case.cfg)
        case.configfile = tf.name


class TestOutputDirSkeleton(OutputNamingConvention):

    def mkdir(self):
        if not os.path.isdir(self.dirname):
            os.mkdir(self.dirname)

    def create_md5sum_file(self, md5s):
        writemd5sums(self.MD5SUMS, md5s)

    def create_expected_docs(self):
        for name in self.expected:
            fname = getattr(self, name)
            with open(fname, 'w'):
                pass


class TestSourceDocSkeleton(object):

    def __init__(self, dirname):
        if isinstance(dirname, list):
            dirname = dirname[0]
        if not os.path.abspath(dirname):
            raise Exception("Please use absolute path in unit tests....")
        self.dirname = dirname
        if not os.path.isdir(self.dirname):
            os.mkdir(self.dirname)
        self.md5s = dict()

    def copytree(self, source):
        dst = opj(self.dirname, opb(source))
        shutil.copytree(source, dst)

    def create_stale(self, fname):
        l = list(self.md5s[fname])
        random.shuffle(l)
        if l == self.md5s[fname]:
            self.invalidate_checksum(fname)
        self.md5s[fname] = ''.join(l)

    @property
    def md5sums(self):
        return self.md5s

    def addsourcefile(self, filename, content):
        fname = os.path.join(self.dirname, filename)
        if os.path.isfile(content):
            shutil.copy(content, fname)
        else:
            with codecs.open(fname, 'w', encoding='utf-8') as f:
                f.write(content)
        relpath = os.path.relpath(fname, start=self.dirname)
        self.md5s[relpath] = md5file(fname)


class TestInventoryBase(unittest.TestCase):

    def setUp(self):
        self.makeTempdir()
        tldp.config.DEFAULT_CONFIGFILE = None
        self.config, _ = tldp.config.collectconfiguration('ldptool', [])
        c = self.config
        c.pubdir = os.path.join(self.tempdir, 'outputs')
        c.builddir = os.path.join(self.tempdir, 'builddir')
        c.sourcedir = os.path.join(self.tempdir, 'sources')
        argv = list()
        argv.extend(['--builddir', c.builddir])
        argv.extend(['--pubdir', c.pubdir])
        argv.extend(['--sourcedir', c.sourcedir])
        self.argv = argv
        # -- and make some directories
        for d in (c.sourcedir, c.pubdir, c.builddir):
            if not os.path.isdir(d):
                os.mkdir(d)
        c.sourcedir = [c.sourcedir]

    def tearDown(self):
        self.removeTempdir()

    def makeTempdir(self):
        self.tempdir = mkdtemp(prefix='tldp-test-')

    def removeTempdir(self):
        shutil.rmtree(self.tempdir)

    def add_stale(self, stem, ex):
        c = self.config
        mysource = TestSourceDocSkeleton(c.sourcedir)
        fname = stem + ex.ext
        mysource.addsourcefile(fname, ex.filename)
        mysource.create_stale(fname)
        myoutput = TestOutputDirSkeleton(os.path.join(c.pubdir, stem), stem)
        myoutput.mkdir()
        myoutput.create_expected_docs()
        myoutput.create_md5sum_file(mysource.md5sums)

    def add_broken(self, stem, ex):
        c = self.config
        mysource = TestSourceDocSkeleton(c.sourcedir)
        fname = stem + ex.ext
        mysource.addsourcefile(fname, ex.filename)
        myoutput = TestOutputDirSkeleton(os.path.join(c.pubdir, stem), stem)
        myoutput.mkdir()
        myoutput.create_expected_docs()
        myoutput.create_md5sum_file(mysource.md5sums)
        prop = random.choice(myoutput.expected)
        fname = getattr(myoutput, prop, None)
        assert fname is not None
        os.unlink(fname)

    def add_new(self, stem, ex, content=None):
        c = self.config
        mysource = TestSourceDocSkeleton(c.sourcedir)
        if content:
            mysource.addsourcefile(stem + ex.ext, content)
        else:
            mysource.addsourcefile(stem + ex.ext, ex.filename)

    def add_unknown(self, stem, ext, content=None):
        c = self.config
        mysource = TestSourceDocSkeleton(c.sourcedir)
        if content:
            mysource.addsourcefile(stem + ext, content)
        else:
            mysource.addsourcefile(stem + ext, '')

    def add_orphan(self, stem, ex):
        c = self.config
        myoutput = TestOutputDirSkeleton(os.path.join(c.pubdir, stem), stem)
        myoutput.mkdir()
        myoutput.create_expected_docs()

    def add_published(self, stem, ex):
        c = self.config
        mysource = TestSourceDocSkeleton(c.sourcedir)
        mysource.addsourcefile(stem + ex.ext, ex.filename)
        myoutput = TestOutputDirSkeleton(os.path.join(c.pubdir, stem), stem)
        myoutput.mkdir()
        myoutput.create_expected_docs()
        myoutput.create_md5sum_file(mysource.md5sums)

    def add_docbooksgml_support_to_config(self):
        c = self.config
        c.docbooksgml_collateindex = opj(extras, 'collateindex.pl')
        c.docbooksgml_ldpdsl = opj(extras, 'dsssl', 'ldp.dsl')

    def add_docbook4xml_xsl_to_config(self):
        c = self.config
        c.docbook4xml_xslprint = opj(extras, 'xsl', 'tldp-print.xsl')
        c.docbook4xml_xslsingle = opj(extras, 'xsl', 'tldp-one-page.xsl')
        c.docbook4xml_xslchunk = opj(extras, 'xsl', 'tldp-chapters.xsl')

#
# -- end of file
