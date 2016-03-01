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


def detail(config, docs, inv, **kwargs):
    if inv is None:
        inv = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
    if not docs:
        docs = inv.work.values()
    width = Namespace()
    width.status = max([len(x) for x in status_types])
    width.stem = max([len(x) for x in inv.source.keys()])
    # -- if user just said "list" with no args, then give the user something
    #    sane, "all"; it would make sense for this to be "work", too, but
    #    "all" seems to be less surprising
    #
    for doc in docs:
        stdout = kwargs.get('file', sys.stdout)
        doc.detail(width, config.verbose, file=stdout)
    return 0


def build(config, docs, inv, **kwargs):
    if inv is None:
        inv = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
    if not docs:
        docs = inv.work.values()
    for source in docs:
        if not isinstance(source, tldp.sources.SourceDocument):
            logger.info("%s skipping, no source for orphan", source.stem)
            continue
        if not source.output:
            dirname = os.path.join(config.pubdir, source.stem)
            source.output = tldp.outputs.OutputDirectory(dirname)
        if not source.doctype:
            logger.warning("%s skipping document of unknown doctype",
                           source.stem)
            continue
        output = source.output
        runner = source.doctype(source=source, output=output, config=config)
        runner.generate()
    return 0


# def script(config, docs, inv, **kwargs):
#     return 0


def getDocumentNames(args):
    sought = set()
    for arg in args:
        doc = arg_issourcedoc(arg)
        if doc is not None:
            sought.add(doc)
    remainder = set(args).difference(sought)
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
    sought = set()
    for cls in tldp.typeguesser.knowndoctypes:
        if cls.__name__.lower() in args:
            sought.add(cls)
    remainder = set(args).difference(sought)
    return sought, remainder


def getStemNames(config, stati, args, inv=None):
    if inv is None:
        inv = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
    sought = set()
    for stem, doc in inv.all.items():
        if stem in args:
            sought.add(doc)
        if doc.status in stati:
            sought.add(doc)
    soughtstems = [x.stem for x in sought]
    remainder = set(args).difference(soughtstems)
    return sought, remainder, inv


def skipDocuments(config, docs, inv):
    if not docs:
        if inv is None:
            inv = tldp.inventory.Inventory(config.pubdir, config.sourcedir)
        docs = inv.all.values()
    included = list()
    excluded = list()
    skip_stati, remainder = getStatusNames(config.skip)
    skip_doctypes, skip_stems = getDocumentClasses(remainder)
    for doc in docs:
        stem = doc.stem
        if hasattr(doc, 'doctype'):
            if doc.doctype in skip_doctypes:
                logger.info("%s skipping doctype %s", stem, doc.doctype)
                excluded.append(doc)
                continue
        if doc.status in skip_stati:
            logger.info("%s skipping status %s", stem, doc.status)
            excluded.append(doc)
            continue
        if doc.stem in skip_stems:
            logger.info("%s skipping stem %s", stem, stem)
            excluded.append(doc)
            continue
        included.append(doc)
    return included, excluded

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

    # -- summary does not require any args
    if config.summary:

        if args:
            return "Unknown args received for --summary: " + ' '.join(args)
        if not config.pubdir:
            return "Option --pubdir (and --sourcedir) required for --summary."
        if not config.sourcedir:
            return "Option --sourcedir (and --pubdir) required for --summary."

        return summary(config)

    # -- args can be a mix of full paths to documents (file or directory)
    #    stem names (for operating on inventory) and status_type names
    #
    # -- sort them out into each of the different types
    #
    docs = list()
    inv = None
    if args:
        rawdocs, remainder = getDocumentNames(args)
        logger.debug("args included %d documents in filesystem: %r",
                     len(rawdocs), rawdocs)
        if rawdocs:
            for doc in rawdocs:
                docs.append(tldp.sources.SourceDocument(doc))

        if remainder:
            stati, remainder = getStatusNames(remainder)
            logger.debug("args included %d status type args: %r",
                         len(stati), stati)

        if remainder or stati:
            logger.debug("Checking inventory (%d stems, %d status_classes).",
                         len(remainder), len(stati))
            if not config.pubdir:
                return " --pubdir (and --sourcedir) required for inventory."
            if not config.sourcedir:
                return " --sourcedir (and --pubdir) required for inventory."

            stems, remainder, inv = getStemNames(config, stati, remainder)
            if stems:
                for doc in stems:
                    docs.append(doc)

        if remainder:
            return "Unknown argument (not stem, file nor status_class): " \
                   + ' '.join(remainder)

    if config.skip:
        docs, excluded = skipDocuments(config, docs, inv)

    # -- one last check to see that config.pubdir and config.sourcedir are set
    #    appropriately; before we try to use them
    #
    if not inv:
        if not config.pubdir:
            return " --pubdir (and --sourcedir) required for inventory."
        if not config.sourcedir:
            return " --sourcedir (and --pubdir) required for inventory."

    if config.detail:
        return detail(config, docs, inv)

    if config.script:
        return script(config, docs, inv)

    if not config.build:
        logger.info("Assuming --build, since no other action was specified...")

    return build(config, docs, inv)

def main():
    sys.exit(run(sys.argv[1:]))

if __name__ == '__main__':
    main()

#
# -- end of file
