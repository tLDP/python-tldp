#! /usr/bin/python

from __future__ import absolute_import, division, print_function

import copy

from .utils import logger, statfiles, max_mtime, mtime_gt

from .sources import SourceCollection
from .outputs import OutputCollection

from argparse import Namespace


class Inventory(object):

    def __init__(self, pubdir, sourcedirs):
        self.outputs = OutputCollection(pubdir)
        self.sources = SourceCollection(sourcedirs)
        s = copy.deepcopy(self.sources)
        o = copy.deepcopy(self.outputs)
        sset = set(s.keys())
        oset = set(o.keys())

        self.orphans = OutputCollection()
        for doc in oset.difference(sset):
            self.orphans[doc] = o[doc]
            del o[doc]
            self.orphans[doc].status = 'orphan'
        logger.info("Identified %d orphaned documents: %r.", len(self.orphans),
                    self.orphans.keys())

        self.new = SourceCollection()
        for doc in sset.difference(oset):
            self.new[doc] = s[doc]
            del s[doc]
            self.new[doc].status = 'new'
        logger.info("Identified %d new documents: %r.", len(self.new),
                    self.new.keys())

        # -- sources + outputs should be same size now
        assert len(s) == len(o)
        for stem, odoc in o.items():
            sdoc = s[stem]
            sdoc.output = odoc
            odoc.source = sdoc
            odoc.status = sdoc.status = 'published'
        self.published = s
        logger.info("Identified %d published documents.", len(self.published))

        self.stale = SourceCollection()
        for stem, sdoc in s.items():
            odoc = sdoc.output
            mtime = max_mtime(statfiles(odoc.dirname, odoc.fileset))
            fset = mtime_gt(mtime, statfiles(sdoc.dirname, sdoc.fileset))
            if fset:
                logger.debug("%s stale files %r", stem, fset)
                odoc.status = sdoc.status = 'stale'
                self.stale[stem] = sdoc
        logger.info("Identified %d stale documents: %r.", len(self.stale),
                    self.stale.keys())


def get_sources(sourcedirs):
    return SourceCollection(sourcedirs)


def get_outputs(pubdir):
    return OutputCollection(pubdir)


def print_sources(scollection, config=None):
    if config is None:
        config = Namespace(sep='\t', verbose=0)
    for stem in sorted(scollection.keys(), key=lambda x: x.lower()):
        doc = scollection[stem]
        if config.verbose:
            fields = [doc.stem, doc.status, doc.filename, str(doc.doctype),
                      doc.doctype.formatname]
            fields.extend(sorted(doc.fileset))
            print(config.sep.join(fields))
        else:
            print(doc.stem)


def print_outputs(ocollection, config=None):
    if config is None:
        config = Namespace(sep='\t', verbose=0)
    for stem in sorted(ocollection.keys(), key=lambda x: x.lower()):
        doc = ocollection[stem]
        if config.verbose:
            fields = [doc.stem, doc.status, doc.dirname]
            print(config.sep.join(fields))
        else:
            print(doc.stem)


def list_sources(sourcedirs, config=None):
    s = get_sources(sourcedirs)
    print_sources(s, config)


def list_outputs(pubdir, config=None):
    o = get_outputs(pubdir)
    print_outputs(o, config)


def list_stale(pubdir, sourcedirs, config=None):
    i = Inventory(pubdir, sourcedirs)
    print_sources(i.stale, config)


def list_new(pubdir, sourcedirs, config=None):
    i = Inventory(pubdir, sourcedirs)
    print_sources(i.new, config)


def list_orphans(pubdir, sourcedirs, config=None):
    i = Inventory(pubdir, sourcedirs)
    print_outputs(i.orphans, config)


#
# -- end of file
