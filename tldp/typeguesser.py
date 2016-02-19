#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import inspect

from .utils import logger, makefh
from . import doctypes


def listDoctypes():
    '''returns a list of tldp.doctypes Python classes

    This is the canonical list of doctypes which are recognized and capable of
    being processed into outputs.  See tldp.doctypes for more information.
    '''
    kdt = list()
    for name, member in inspect.getmembers(doctypes, inspect.isclass):
        logger.debug("Located class %s (%r).", name, member)
        kdt.append(member)
    logger.debug("Capable of handling %s document classes.", len(kdt))
    return kdt


def guess(thing):
    '''return a tldp.doctype class which is a best guess for document type

    thing: Could be a filename or an open file.

    The guess function will try to guess the document type (doctype) from the
    file extension.  If extension matching produces multiple possible doctype
    matches (e.g. .xml or .sgml), the guess function will then use signature
    matching to find the earliest match in the file for a signature.

    If there are multiple signature matches, it will choose the signature
    matching at the earliest position in the file.

    Bugs/shortcomings:

      * This is only a guesser.
      * When signature matching, it reports first signature it discovers in
        any input file.
      * It could/should read more than 1024 bytes (cf. SignatureChecker)
        especially if it cannot return any result.
      * It could/should use heuristics or something richer than signatures.
    '''
    try:
        f = makefh(thing)
    except TypeError:
        return None

    stem, ext = os.path.splitext(f.name)
    if not ext:
        logger.debug("%s no file extension, skipping %s.", stem, ext)
        return None

    possible = [t for t in knowndoctypes if ext in t.extensions]
    logger.debug("Possible:  %r", possible)
    if not possible:
        logger.debug("%s unknown extension %s.", stem, ext)
        return None

    if len(possible) == 1:
        doctype = possible.pop()
        return doctype

    # -- for this extension, multiple document types, probably SGML, XML
    #
    logger.debug("%s multiple possible doctypes for extension %s on file %s.",
                 stem, ext, f.name)
    for doctype in possible:
        logger.debug("%s extension %s could be %s.", stem, ext, doctype)

    guesses = list()
    for doctype in possible:
        sindex = doctype.signatureLocation(f)
        if sindex is not None:
            guesses.append((sindex, doctype))

    if not guesses:
        logger.warning("%s no matching signature found for %s.",
                       stem, f.name)
        return None
    if len(guesses) == 1:
        _, doctype = guesses.pop()
        return doctype

    # -- OK, this is unusual; we still found multiple document type
    #    signatures.  Seems rare but unlikely, so we should choose the
    #    first signature in the file as the more likely document type.
    #
    guesses.sort()
    logger.info("%s multiple doctype guesses for file %s", stem, f.name)
    for sindex, doctype in guesses:
        logger.info("%s could be %s (sig at pos %s)", stem, doctype, sindex)
    logger.info("%s going to guess %s for %s", stem, doctype, f.name)
    _, doctype = guesses.pop(0)
    return doctype


knowndoctypes = listDoctypes()
knownextensions = set()
for x in knowndoctypes:
    knownextensions.update(x.extensions)

#
# -- end of file
