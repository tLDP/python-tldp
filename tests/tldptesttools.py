
from __future__ import absolute_import, division, print_function

import os
import time
import random
import shutil
import unittest
from tempfile import mkdtemp
from tempfile import NamedTemporaryFile as ntf

from tldp.config import collectconfiguration
from tldp.outputs import OutputNamingConvention


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
        f = ntf(prefix=case.tag, suffix='.cfg', dir=self.tempdir, delete=False)
        f.write(case.cfg)
        f.close()
        case.configfile = f.name


class TestOutputDirSkeleton(OutputNamingConvention):

    def mkdir(self):
        if not os.path.isdir(self.dirname):
            os.mkdir(self.dirname)

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

    def addsourcefile(self, filename, content):
        fname = os.path.join(self.dirname, filename)
        if os.path.isfile(content):
            shutil.copy(content, fname)
        else:
            with open(fname, 'w') as f:
                f.write(content)


class TestInventoryBase(unittest.TestCase):

    def setUp(self):
        self.makeTempdir()
        self.config, _ = collectconfiguration('ldptool', [])
        c = self.config
        c.pubdir = os.path.join(self.tempdir, 'outputs')
        c.builddir = os.path.join(self.tempdir, 'builddir')
        c.sourcedir = os.path.join(self.tempdir, 'sources')
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
        myoutput = TestOutputDirSkeleton(os.path.join(c.pubdir, stem), stem)
        myoutput.mkdir()
        myoutput.create_expected_docs()
        time.sleep(0.001)
        mysource = TestSourceDocSkeleton(c.sourcedir)
        mysource.addsourcefile(stem + ex.ext, ex.filename)

    def add_broken(self, stem, ex):
        c = self.config
        mysource = TestSourceDocSkeleton(c.sourcedir)
        mysource.addsourcefile(stem + ex.ext, ex.filename)
        myoutput = TestOutputDirSkeleton(os.path.join(c.pubdir, stem), stem)
        myoutput.mkdir()
        myoutput.create_expected_docs()
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

#
# -- end of file
