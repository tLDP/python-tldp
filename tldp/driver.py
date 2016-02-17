#! /usr/bin/python

from __future__ import absolute_import, division, print_function

from .utils import logger, statfiles, max_mtime, mtime_gt

from .sources import SourceCollection
from .outputs import OutputCollection

from argparse import Namespace


def get_outputs(pubdir):
    o = OutputCollection(pubdir)
    return o


def get_sources(sourcedirs):
    s = SourceCollection(sourcedirs)
    return s


def get_differences_intersections(pubdir, sourcedirs):
    s = get_sources(sourcedirs)
    o = get_outputs(pubdir)
    sset = set(s.keys())
    oset = set(o.keys())

    orphans = OutputCollection()
    for doc in oset.difference(sset):
        orphans[doc] = o[doc]
        del o[doc]
        orphans[doc].status = 'orphan'

    new = SourceCollection()
    for doc in sset.difference(oset):
        new[doc] = s[doc]
        del s[doc]
        new[doc].status = 'new'

    return orphans, new, s, o


def get_published(pubdir, sourcedirs):
    _, _, s, o = get_differences_intersections(pubdir, sourcedirs)
    assert len(s) == len(o)
    for stem, odoc in o.items():
        sdoc = s[stem]
        sdoc.output = odoc
        odoc.source = sdoc
        odoc.status = sdoc.status = 'published'
    return s


def get_stale(pubdir, sourcedirs):
    s = get_published(pubdir, sourcedirs)
    stale = SourceCollection()
    for stem, sdoc in s.items():
        odoc = sdoc.output
        mtime = max_mtime(statfiles(odoc.dirname, odoc.fileset))
        fset = mtime_gt(mtime, statfiles(sdoc.dirname, sdoc.fileset))
        if fset:
            logger.debug("%s stale files %r", stem, fset)
            odoc.status = sdoc.status = 'stale'
            stale[stem] = sdoc
    return stale


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
    s = get_stale(pubdir, sourcedirs)
    print_sources(s, config)


def list_new(pubdir, sourcedirs, config=None):
    _, s, _, _ = get_differences_intersections(pubdir, sourcedirs)
    print_sources(s, config)


def list_orphans(pubdir, sourcedirs, config=None):
    o, _, _, _ = get_differences_intersections(pubdir, sourcedirs)
    print_outputs(o, config)


#
# -- end of file
