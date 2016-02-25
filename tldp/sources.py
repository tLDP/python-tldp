#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import sys
import errno
import logging
logger = logging.getLogger(__name__)

from tldp.ldpcollection import LDPDocumentCollection

from tldp.utils import statfiles, stem_and_ext
from tldp.typeguesser import guess, knownextensions


def scansourcedirs(dirnames):
    '''return a dict() of all SourceDocuments discovered in dirnames
    dirnames:  a list of directories containing SourceDocuments.

    scansourcedirs ensures it is operating on the absolute filesystem path for
    each of the source directories.

    If any of the supplied dirnames does not exist as a directory, the function
    will log the missing source directory names and then will raise an IOError
    and quit.

    For each document that it finds in a source directory, it creates a
    SourceDocument entry using the stem name as a key.

    The rules for identifying possible SourceDocuments go as follows.

      - Within any source directory, a source document can consist of a single
        file with an extension or a directory.

      - If the candidate entry is a directory, then, the stem is the full
        directory name, e.g. Masquerading-Simple-HOWTO

      - If the candidate entry is a file, the stem is the filename minus
        extension, e.g. Encrypted-Root-Filesystem-HOWTO

    Because the function accepts (and will scan) many source directories, it
    is possible that there will be stem name collisions.  If it discovers a
    stem collision, SourceCollection will issue a warning and skip the
    duplicated stem(s).  [It also tries to process the source directories and
    candidates in a stable order between runs.]
    '''
    found = dict()
    dirs = [os.path.abspath(x) for x in dirnames]
    results = [os.path.exists(x) for x in dirs]

    if not all(results):
        for result, sdir in zip(results, dirs):
            logger.critical("Source collection dir must already exist: %s",
                            sdir)
        raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), sdir)

    for sdir in sorted(dirs):
        for fname in sorted(os.listdir(sdir)):
            candidates = list()
            possible = os.path.join(sdir, fname)
            if os.path.isfile(possible):
                candidates.append(SourceDocument(possible))
            elif os.path.isdir(possible):
                possible = sourcedoc_fromdir(possible)
                if possible:
                    candidates.append(SourceDocument(possible))
            else:
                logger.warning("Skipping non-directory, non-plain file %s",
                               possible)
                continue
            for candy in candidates:
                if candy.stem in found:
                    dup = found[candy.stem].filename
                    logger.warning("Ignoring duplicate is %s", candy.filename)
                    logger.warning("Existing dup-entry is %s", dup)
                else:
                    found[candy.stem] = candy
    logger.debug("Discovered %s documents total", len(found))
    return found


def sourcedoc_fromdir(dirname):
    candidates = list()
    stem, _ = stem_and_ext(dirname)
    parentdir = os.path.dirname(dirname)
    for ext in knownextensions:
        possible = os.path.join(parentdir, stem, stem + ext)
        if os.path.isfile(possible):
            candidates.append(possible)
    if len(candidates) > 1:
        logger.warning("%s multiple document choices in dir %s, bailing....",
                       stem, dirname)
        raise Exception("multiple document choices in " + dirname)
    elif len(candidates) == 0:
        return None
    else:
        return candidates.pop()


class SourceCollection(LDPDocumentCollection):
    '''a dict-like container for SourceDocument objects

    The key in the SourceCollection is the stem name of the document, which
    allows convenient access and guarantees non-collision.

    The use of the stem as a key works conveniently with the
    OutputCollection which uses the same strategy on OutputDirectory.
    '''
    def __init__(self, dirnames=None):
        '''construct a SourceCollection

        delegates most responsibility to function scansourcedirs
        '''
        if dirnames is None:
            return
        self.update(scansourcedirs(dirnames))


class SourceDocument(object):
    '''a class providing a container for each set of source documents
    '''
    def __repr__(self):
        return '<%s:%s (%s)>' % \
               (self.__class__.__name__, self.filename, self.doctype)

    def __init__(self, filename):
        '''construct a SourceDocument

        filename is a required parameter

        The filename is the main (and sometimes sole) document representing
        the source of the LDP HOWTO or Guide.  It is the document that is
        passed by name to be handled by any document processing toolchains
        (see also tldp.doctypes).

        Each instantiation will raise an IOERror if the supplied filename does
        not exist or if the filename isn't a file (symlink is fine, directory
        or fifo is not).

        The remainder of the instantiation will set attributes that are useful
        later in the processing phase, for example, stem, status, enclosing
        directory name and file extension.

        There are two important attributes.  First, the document type guesser
        will try to infer the doctype (from file extension and signature).
        Note that it is not a fatal error if document type cannot be guessed,
        but the document will not be able to be processed.  Second, it is
        useful during the decision-making process to know if any of the source
        files are newer than the output files. Thus, the stat() information
        for every file in the source document directory (or just the single
        source document file) will be collected.
        '''
        self.filename = os.path.abspath(filename)
        if not os.path.exists(self.filename):
            logger.critical("Missing source document: %s", self.filename)
            raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), self.filename)
        if not os.path.isfile(self.filename):
            logger.critical("Source document is not a plain file: %s", self.filename)
            raise TypeError("Wrong type, not a plain file: " + self.filename)

        self.doctype = guess(self.filename)
        self.status = 'source'
        self.output = None
        self.newer = set()
        self.dirname, self.basename = os.path.split(self.filename)
        self.stem, self.ext = stem_and_ext(self.basename)
        parentbase = os.path.basename(self.dirname)
        logger.debug("%s found source %s", self.stem, self.filename)
        if parentbase == self.stem:
            self.statinfo = statfiles(self.dirname, relative=self.dirname)
        else:
            self.statinfo = statfiles(self.filename, relative=self.dirname)

    def detail(self, widths, verbose, file=sys.stdout):
        '''
        '''
        template = '{s.status:{w.status}} {s.stem:{w.stem}}'
        outstr = template.format(s=self, w=widths)
        print(outstr)
        if verbose:
            for f in self.newer:
                fname = os.path.join(self.dirname, f)
                print('  newer file {}'.format(fname))
            if self.output:
                for f in self.output.missing:
                    print('  missing file {}'.format(f))

#
# -- end of file
