#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import sys
import logging
from argparse import Namespace

import tldp
import tldp.typeguesser

from tldp.inventory import status_classes, status_types
from tldp.utils import arg_isloglevel
from tldp.sources import arg_issourcedoc

logformat = '%(levelname)-9s %(name)s %(filename)s#%(lineno)s %(funcName)s %(message)s'
logging.basicConfig(stream=sys.stderr, format=logformat, level=logging.ERROR)
logger = logging.getLogger(__name__)


def summary(config, inv=None, **kwargs):
    if inv is None:
        inv = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
    file = kwargs.get('file', sys.stdout)
    width = Namespace()
    width.status = max([len(x) for x in status_types])
    width.count = len(str(len(inv.source.keys())))
    for status in status_types:
        if status == 'all':
            continue
        count = len(getattr(inv, status, 0))
        s = '{0:{w.status}}  {1:{w.count}}  '.format(status, count, w=width)
        print(s, end="", file=file)
        if config.verbose:
            print(', '.join(getattr(inv, status).keys()), file=file)
        else:
            abbrev = getattr(inv, status).keys()
            s = ''
            if abbrev:
                s = s + abbrev.pop(0)
                while abbrev and len(s) < 50:
                    s = s + ', ' + abbrev.pop(0)
                if abbrev:
                    s = s + ', and %d more ...' % (len(abbrev))
            print(s, file=file)
    return 0


def detail(config, docs, **kwargs):
    width = Namespace()
    width.status = max([len(x) for x in status_types])
    width.stem = max([len(x.stem) for x in docs])
    # -- if user just said "list" with no args, then give the user something
    #    sane, "all"; it would make sense for this to be "work", too, but
    #    "all" seems to be less surprising
    #
    for doc in docs:
        stdout = kwargs.get('file', sys.stdout)
        doc.detail(width, config.verbose, file=stdout)
    return 0


def build(config, docs, **kwargs):
    for x, source in enumerate(docs, 1):
        if not isinstance(source, tldp.sources.SourceDocument):
            logger.info("%s (%d of %d) skipping, no source for orphan",
                        source.stem, x, len(docs))
            continue
        if not source.output:
            dirname = os.path.join(config.pubdir, source.stem)
            source.output = tldp.outputs.OutputDirectory(dirname)
        if not source.doctype:
            logger.warning("%s (%d of %d) skipping unknown doctype",
                           source.stem, x, len(docs))
            continue
        output = source.output
        runner = source.doctype(source=source, output=output, config=config)
        logger.info("%s (%d of %d) initiating build",
                    source.stem, x, len(docs))
        runner.generate()
    return 0


# def script(config, docs, inv, **kwargs):
#     return 0


def getDocumentNames(args):
    sought = list()
    for arg in args:
        doc = arg_issourcedoc(arg)
        if doc is not None:
            sought.append(doc)
        else:
            sought.append(None)
    remainder = set([y for x, y in zip(sought, args) if not x])
    sought = set(filter(None, sought))
    return sought, remainder


def getStatusNames(args):
    found = set()
    sought = set()
    for arg in args:
        stati = status_classes.get(arg, None)
        if stati:
            sought.update(stati)
            found.add(arg)
    remainder = set(args).difference(found)
    return sought, remainder


def getDocumentClasses(args):
    largs = [x.lower() for x in args]
    sought = list()
    for cls in tldp.typeguesser.knowndoctypes:
        if cls.__name__.lower() in largs:
            sought.append(cls)
        else:
            sought.append(None)
    remainder = set([y for x, y in zip(sought, args) if not x])
    sought = set(filter(None, sought))
    return sought, remainder


def getDocumentsByStems(docs, args):
    sought = set()
    for doc in docs:
        if doc.stem in args:
            sought.add(doc)
    soughtstems = [x.stem for x in sought]
    remainder = set(args).difference(soughtstems)
    return sought, remainder


def getDocumentsByStatus(docs, stati):
    sought = set()
    for doc in docs:
        if doc.status in stati:
            sought.add(doc)
    return sought


def processSkips(config, docs):
    included = set()
    excluded = set()
    skip_stati, remainder = getStatusNames(config.skip)
    skip_doctypes, skip_stems = getDocumentClasses(remainder)
    for doc in docs:
        stem = doc.stem
        if hasattr(doc, 'doctype'):
            if doc.doctype in skip_doctypes:
                logger.info("%s skipping doctype %s", stem, doc.doctype)
                excluded.add(doc)
                continue
        if doc.status in skip_stati:
            logger.info("%s skipping status %s", stem, doc.status)
            excluded.add(doc)
            continue
        if doc.stem in skip_stems:
            logger.info("%s skipping stem %s", stem, stem)
            excluded.add(doc)
            continue
        included.add(doc)
    return included, excluded


def extractExplicitDocumentArgs(config, args):
    docs = set()
    rawdocs, remainder = getDocumentNames(args)
    logger.debug("args included %d documents in filesystem: %r",
                 len(rawdocs), rawdocs)
    for doc in rawdocs:
        docs.add(tldp.sources.SourceDocument(doc))
    return docs, remainder


def run(argv):
    # -- may want to see option parsing, so set --loglevel as
    #    soon as possible
    if '--loglevel' in argv:
        levelarg = 1 + argv.index('--loglevel')
        level = arg_isloglevel(argv[levelarg])
        # -- set the root logger's level
        logging.getLogger().setLevel(level)

    # -- produce a configuration from CLI, ENV and CFG
    #
    tag = 'ldptool'
    config, args = tldp.config.collectconfiguration(tag, argv)

    logger.debug("Received the following configuration:")
    for param, value in sorted(vars(config).items()):
        logger.debug("  %s = %r", param, value)
    logger.debug("  args: %r", args)

    # -- summary does not require any args
    if config.summary:

        if args:
            return "Unknown args received for --summary: " + ' '.join(args)
        if not config.pubdir:
            return "Option --pubdir (and --sourcedir) required for --summary."
        if not config.sourcedir:
            return "Option --sourcedir (and --pubdir) required for --summary."

        return summary(config)

    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    # -- argument handling logic; try to avoid creating an inventory unless it
    #    is necessary
    #
    workset, remainder = extractExplicitDocumentArgs(config, args)
    stati, remainder = getStatusNames(remainder)
    if len(workset):
        logger.info("Added %d explicit file paths from args.", len(workset))

    need_inventory = False
    if remainder or stati:
        need_inventory = True
    if not workset:
        need_inventory = True

    # -- by default, we only --list, --script or --build on work-to-be-done
    #    so, if there have been no special arguments at this point, we will
    #    simply grab the work to be done; see below the line that says:
    #
    #      docs = inv.work.values()
    #
    # -- also make one last check to see that config.pubdir and
    #    config.sourcedir are set appropriately; just before creating an
    #    Inventory
    #
    if need_inventory:
        if not config.pubdir:
            return " --pubdir (and --sourcedir) required for inventory."
        if not config.sourcedir:
            return " --sourcedir (and --pubdir) required for inventory."
        inv = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
    else:
        inv = None

    if stati:
        oldsize = len(workset)
        for status in stati:
            collection = getattr(inv, status)
            assert isinstance(collection, tldp.sources.SourceCollection)
            workset.update(collection.values())
        growth = len(workset) - oldsize
        if growth:
            logger.info("Added %d docs, found by status class .", growth)

    unknownargs = None
    if remainder:
        docs, unknownargs = getDocumentsByStems(inv.work.values(), remainder)
        workset.update(docs)
        logger.info("Added %d docs, found by stem name.", len(docs))

    if unknownargs:
        return "Unknown argument (not stem, file nor status_class): " \
               + ' '.join(remainder)

    if not workset:
        workset.update(inv.work.values())

    workset, excluded = processSkips(config, workset)

    if not workset:
        return "No work to do."
    
    docs = sorted(workset, key=lambda x: x.stem.lower())

    if config.detail:
        return detail(config, docs)

    if config.script:
        return script(config, docs)

    if not config.build:
        logger.info("Assuming --build, since no other action was specified...")

    return build(config, docs)


def main():
    sys.exit(run(sys.argv[1:]))

if __name__ == '__main__':
    main()

#
# -- end of file
