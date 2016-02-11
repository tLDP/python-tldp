#! /usr/bin/python

from __future__ import print_function

import os
import inspect

from . import doctypes
from .utils import logger


def makefh(thing):
    if isinstance(thing, file):
        f = thing
    elif isinstance(thing, str) and os.path.isfile(thing):
        f = open(thing)
    else:
        raise TypeError("Cannot make file from type %s of %r" %
                        (type(thing), thing,))
    return f


def listDoctypes():
    knowndoctypes = list()
    for name, member in inspect.getmembers(doctypes, inspect.isclass):
        logger.info("Located class %s (%r).", name, member)
        knowndoctypes.append(member)
    logger.info("Capable of handling %s document classes.", len(knowndoctypes))
    return knowndoctypes


def guess(thing):
    try:
        fin = makefh(thing)
    except TypeError:
        return None

    _, ext = os.path.splitext(fin.name)
    possible = [t for t in knowndoctypes if ext in t.extensions]
    if not possible:
        return None
    if len(possible) == 1:
        doctype = possible.pop()
        return doctype

    # -- for this extension, multiple document types, probably SGML, XML
    #
    logger.info("Extension is %s for %s; multiple possible document types.",
                ext, fin.name)
    for doctype in possible:
        logger.debug("Extension is %s for %s; %s.", ext, fin.name, doctype)

    guesses = list()
    for doctype in possible:
        sindex = doctype.signatureLocation(fin.name, fin)
        if sindex is not None:
            guesses.append((sindex, doctype))

    if not guesses:
        logger.info("Extension is %s for %s; but no matching signature found.",
                    ext, fin.name)
        return None
    if len(guesses) == 1:
        _, doctype = guesses.pop()
        return doctype

    # -- OK, this is unusual; we still found multiple document type
    #    signatures.  Seems rare but unlikely, so we should choose the
    #    first signature in the file as the more likely document type.
    #
    guesses.sort()
    logger.info("Multiple guesses for file %s", fin.name)
    for sindex, doctype in guesses:
        logger.info("Could be %s (file position %s)", doctype, sindex)
    logger.info("Going to guess that it is %s", doctype)
    _, doctype = guesses.pop()
    return doctype


knowndoctypes = listDoctypes()
knownextensions = set()
for x in knowndoctypes:
    knownextensions.update(x.extensions)

#
# -- end of file
