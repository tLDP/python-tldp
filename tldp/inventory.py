#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import copy

from .utils import logger, max_mtime, mtime_gt

from .sources import SourceCollection
from .outputs import OutputCollection

from argparse import Namespace

# -- any individual document (source or output) will have a status
#    from the following list of status_types
#
status_types = [
                'source',
                'output',
                'published',
                'new',
                'orphan',
                'broken',
                'stale',
                ]

# -- the user probably doesn't usually care (too much) about listing
#    every single published document and source document, but is probably
#    mostly interested in specific documents grouped by status; so the
#    status_classes are just sets of status_types
#
status_classes = dict(zip(status_types, [[x] for x in status_types]))
status_classes['outputs'] = ['output']
status_classes['sources'] = ['source']
status_classes['problems'] = ['orphan', 'broken', 'stale']
status_classes['work'] = ['new', 'orphan', 'broken', 'stale']
status_classes['orphans'] = ['orphan']
status_classes['orphaned'] = ['orphan']
status_classes['all'] = ['published', 'new', 'orphan', 'broken', 'stale']


class Inventory(object):
    '''a container for classifying documents by their status

    Every SourceDocument has no more than one matching OutputDirectory.

    The Inventory class encodes the logic for identifying the following
    different status possibilities for an arbitrary set of SourceDocuments and
    OutputDirectorys.

    The following are possible values for status:
       - 'source':  a source document before any status detection
       - 'output':  an output document before any status detection
       - 'new':  a source document without any matching output stem
       - 'published':  a pair of source/output documents with matching stems
       - 'orphan':  an output document without any matching source stem
       - 'broken':  a published document with missing output files
       - 'stale':  a published document with new(er) source files

    The Inventory object is intended to be used to identify work that needs to
    be done on individual source documents to produce up-to-date output
    documents.
    '''
    def __repr__(self):
        return '<%s: %d published, %d orphan, %d new, %d stale, %d broken>' % (
               self.__class__.__name__,
               len(self.published),
               len(self.orphan),
               len(self.new),
               len(self.stale),
               len(self.broken),
               )

    def __init__(self, pubdir, sourcedirs):
        '''construct an Inventory

        pubdir: path to the OutputCollection

        sourcedirs: a list of directories which could be passed to the
          SourceCollection object; essentially a directory containing
          SourceDocuments; for example LDP/LDP/howto/linuxdoc and
          LDP/LDP/guide/docbook
        '''
        self.output = OutputCollection(pubdir)
        self.source = SourceCollection(sourcedirs)
        s = copy.deepcopy(self.source)
        o = copy.deepcopy(self.output)
        sset = set(s.keys())
        oset = set(o.keys())

        # -- orphan identification
        #
        self.orphan = OutputCollection()
        for doc in oset.difference(sset):
            self.orphan[doc] = o[doc]
            del o[doc]
            self.orphan[doc].status = 'orphan'
        logger.info("Identified %d orphan documents: %r.", len(self.orphan),
                    self.orphan.keys())

        # -- unpublished ('new') identification
        #
        self.new = SourceCollection()
        for doc in sset.difference(oset):
            self.new[doc] = s[doc]
            del s[doc]
            self.new[doc].status = 'new'
        logger.info("Identified %d new documents: %r.", len(self.new),
                    self.new.keys())

        # -- published identification; source and output should be same size
        assert len(s) == len(o)
        for stem, odoc in o.items():
            sdoc = s[stem]
            sdoc.output = odoc
            odoc.source = sdoc
            sdoc.status = sdoc.output.status = 'published'
        self.published = s
        logger.info("Identified %d published documents.", len(self.published))

        # -- stale identification
        #
        self.stale = SourceCollection()
        for stem, sdoc in s.items():
            odoc = sdoc.output
            mtime = max_mtime(odoc.statinfo)
            fset = mtime_gt(mtime, sdoc.statinfo)
            if fset:
                sdoc.newer = fset
                for f in fset:
                    logger.debug("%s found updated source file %s", stem, f)
                odoc.status = sdoc.status = 'stale'
                self.stale[stem] = sdoc
        logger.info("Identified %d stale documents: %r.", len(self.stale),
                    self.stale.keys())

        # -- stale identification
        #
        self.broken = SourceCollection()
        for stem, sdoc in s.items():
            if not sdoc.output.iscomplete:
                self.broken[stem] = sdoc
                sdoc.status = sdoc.output.status = 'broken'
        logger.info("Identified %d broken documents: %r.", len(self.broken),
                    self.broken.keys())


def get_sources(sourcedirs):
    return SourceCollection(sourcedirs)


def get_outputs(pubdir):
    return OutputCollection(pubdir)


def print_sources(scollection, config=None):
    if config is None:
        config = Namespace(sep='\t', verbose=0)
    for stem in scollection.keys():
        doc = scollection[stem]
        if config.verbose:
            fields = [doc.stem, doc.status]
            fields.append(str(len(doc.statinfo)) + ' source files')
            fields.append(doc.filename)
            fields.extend(doc.doctype.formatname)
            fields.extend(str(doc.doctype))
            print(config.sep.join(fields))
        else:
            print(doc.stem)


def print_outputs(ocollection, config=None):
    if config is None:
        config = Namespace(sep='\t', verbose=0)
    for stem in ocollection.keys():
        doc = ocollection[stem]
        if config.verbose:
            fields = [doc.stem, doc.status, doc.dirname]
            fields.append(str(len(doc.statinfo)) + ' files')
            print(config.sep.join(fields))
        else:
            print(doc.stem)


#
# -- end of file
