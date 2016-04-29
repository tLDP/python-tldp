#! /usr/bin/python
# -*- coding: utf8 -*-
#
# Copyright (c) 2016 Linux Documentation Project

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import copy
import logging
from collections import OrderedDict

from tldp.sources import SourceCollection
from tldp.outputs import OutputCollection

logger = logging.getLogger(__name__)

# -- any individual document (source or output) will have a status
#    from the following list of status_types
#
stypes = OrderedDict()
stypes['source'] = 'found in source repository'
stypes['output'] = 'found in output repository'
stypes['published'] = 'matching stem in source/output; doc is up to date'
stypes['stale'] = 'matching stem in source/output; but source is newer'
stypes['orphan'] = 'stem located in output, but no source found (i.e. old?)'
stypes['broken'] = 'output is missing an expected output format (e.g. PDF)'
stypes['new'] = 'stem located in source, but missing in output; unpublished'

status_types = stypes.keys()

# -- the user probably doesn't usually care (too much) about listing
#    every single published document and source document, but is probably
#    mostly interested in specific documents grouped by status; so the
#    status_classes are just sets of status_types
#
status_classes = OrderedDict(zip(status_types, [[x] for x in status_types]))
status_classes['outputs'] = ['output']
status_classes['sources'] = ['source']
status_classes['orphans'] = ['orphan']
status_classes['orphaned'] = ['orphan']
status_classes['problems'] = ['orphan', 'broken', 'stale']
status_classes['work'] = ['new', 'orphan', 'broken', 'stale']
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
               len(self.broken),)

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
        logger.debug("Identified %d orphan documents: %r.", len(self.orphan),
                     self.orphan.keys())

        # -- unpublished ('new') identification
        #
        self.new = SourceCollection()
        for doc in sset.difference(oset):
            self.new[doc] = s[doc]
            del s[doc]
            self.new[doc].status = 'new'
        logger.debug("Identified %d new documents: %r.", len(self.new),
                     self.new.keys())

        # -- published identification; source and output should be same size
        assert len(s) == len(o)
        for stem, odoc in o.items():
            sdoc = s[stem]
            sdoc.output = odoc
            odoc.source = sdoc
            sdoc.status = sdoc.output.status = 'published'
        self.published = s
        logger.debug("Identified %d published documents.", len(self.published))

        # -- broken identification
        #
        self.broken = SourceCollection()
        for stem, sdoc in s.items():
            if not sdoc.output.iscomplete:
                self.broken[stem] = sdoc
                sdoc.status = sdoc.output.status = 'broken'
        logger.debug("Identified %d broken documents: %r.", len(self.broken),
                     self.broken.keys())

        # -- stale identification
        #
        self.stale = SourceCollection()
        for stem, sdoc in s.items():
            odoc = sdoc.output
            omd5, smd5 = odoc.md5sums, sdoc.md5sums
            if omd5 != smd5:
                logger.debug("%s differing MD5 sets %r %r", stem, smd5, omd5)
                changed = set()
                for gone in set(omd5.keys()).difference(smd5.keys()):
                    logger.debug("%s gone %s", stem, gone)
                    changed.add(('gone', gone))
                for new in set(smd5.keys()).difference(omd5.keys()):
                    changed.add(('new', new))
                for sfn in set(smd5.keys()).intersection(omd5.keys()):
                    if smd5[sfn] != omd5[sfn]:
                        changed.add(('changed', sfn))
                for why, sfn in changed:
                    logger.debug("%s differing source %s (%s)", stem, sfn, why)
                odoc.status = sdoc.status = 'stale'
                sdoc.differing = changed
                self.stale[stem] = sdoc
        logger.debug("Identified %d stale documents: %r.", len(self.stale),
                     self.stale.keys())

    def getByStatusClass(self, status_class):
        desired = status_classes.get(status_class, None)
        assert isinstance(desired, list)
        collection = SourceCollection()
        for status_type in desired:
            collection.update(getattr(self, status_type))
        return collection

    @property
    def outputs(self):
        return self.getByStatusClass('outputs')

    @property
    def sources(self):
        return self.getByStatusClass('sources')

    @property
    def problems(self):
        return self.getByStatusClass('problems')

    @property
    def work(self):
        return self.getByStatusClass('work')

    @property
    def orphans(self):
        return self.getByStatusClass('orphans')

    @property
    def orphaned(self):
        return self.getByStatusClass('orphaned')

    @property
    def all(self):
        return self.getByStatusClass('all')

#
# -- end of file
