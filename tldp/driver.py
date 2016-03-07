#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import sys
import logging
import inspect
from argparse import Namespace

from tldp.typeguesser import knowndoctypes
from tldp.sources import SourceDocument, arg_issourcedoc
from tldp.outputs import OutputDirectory
from tldp.inventory import Inventory, status_classes, status_types, stypes
from tldp.config import collectconfiguration
from tldp.utils import arg_isloglevel, arg_isdirectory
from tldp.doctypes.common import preamble, postamble

logformat = '%(levelname)-9s %(name)s %(filename)s#%(lineno)s ' \
     + '%(funcName)s %(message)s'
logging.basicConfig(stream=sys.stderr, format=logformat, level=logging.ERROR)
logger = logging.getLogger(__name__)

# -- error message prefixes
#
ERR_NEEDPUBDIR = "Option --pubdir (and --sourcedir) required "
ERR_NEEDSOURCEDIR = "Option --sourcedir (and --pubdir) required "
ERR_UNKNOWNARGS = "Unknown arguments received: "
ERR_EXTRAARGS = "Extra arguments received: "



def show_doctypes(config, *args, **kwargs):
    if args:
        return ERR_EXTRAARGS + ' '.join(args)
    file = kwargs.get('file', sys.stdout)
    print("Supported source document types:", file=file)
    print(file=file)
    for doctype in knowndoctypes:
        classname = doctype.__name__
        fname = os.path.abspath(inspect.getmodule(doctype).__file__)
        extensions = ', '.join(doctype.extensions)
        print('{}'.format(classname), file=file)
        print('      format name: {}'.format(doctype.formatname), file=file)
        print('    code location: {}'.format(fname), file=file)
        print('  file extensions: {}'.format(extensions), file=file)
        for signature in doctype.signatures:
            print('        signature: {}'.format(signature), file=file)
        print(file=file)
    print(file=file)
    return os.EX_OK


def show_statustypes(config, *args, **kwargs):
    if args:
        return ERR_EXTRAARGS + ' '.join(args)
    file = kwargs.get('file', sys.stdout)
    width = 2 + max([len(x) for x in status_types])
    print("Basic status types:", file=file)
    print(file=file)
    for status, descrip in stypes.items():
        fmt = '{status:>{width}}:  {descrip}'
        text = fmt.format(status=status, descrip=descrip, width=width)
        print(text, file=file)
    print(file=file)
    print("Synonyms and groups:", file=file)
    print(file=file)
    for status, descrip in status_classes.items():
        fmt = '{status:>{width}}:  {descrip}'
        descrip = ', '.join(descrip)
        text = fmt.format(status=status, descrip=descrip, width=width)
        print(text, file=file)
    print(file=file)
    return os.EX_OK


def summary(config, *args, **kwargs):
    if args:
        return ERR_EXTRAARGS + ' '.join(args)
    if not config.pubdir:
        return ERR_NEEDPUBDIR + "for --summary"
    if not config.sourcedir:
        return ERR_NEEDSOURCEDIR + "for --summary"
    file = kwargs.get('file', sys.stdout)
    inv = kwargs.get('inv', None)
    if inv is None:
        inv = Inventory(config.pubdir, config.sourcedir)
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
                while abbrev:
                    if (len(s) + len(abbrev[0])) > 48:
                        break
                    s = s + ', ' + abbrev.pop(0)
                if abbrev:
                    s = s + ', and %d more ...' % (len(abbrev))
            print(s, file=file)
    return os.EX_OK


def detail(config, docs, **kwargs):
    file = kwargs.get('file', sys.stdout)
    width = Namespace()
    width.status = max([len(x) for x in status_types])
    width.stem = max([len(x.stem) for x in docs])
    # -- if user just said "list" with no args, then give the user something
    #    sane, "all"; it would make sense for this to be "work", too, but
    #    "all" seems to be less surprising
    #
    for doc in docs:
        doc.detail(width, config.verbose, file=file)
    return os.EX_OK


def builddir_setup(config):
    if not config.builddir:
        builddir = os.path.dirname(os.path.abspath(config.pubdir))
        builddir = os.path.join(builddir, 'ldp-builddir')
        if not arg_isdirectory(builddir):
            logger.debug("Creating build directory %s.", builddir)
            try:
                os.mkdir(builddir)
            except OSError as e:
                logger.critical("Could not make --builddir %s.", builddir)
                return False, e.errno
        config.builddir = builddir
    if not sameFilesystem(config.pubdir, config.builddir):
        return False, "--pubdir and --builddir must be on the same filesystem"
    return True, None


def build(config, docs, **kwargs):
    if not config.pubdir:
        return ERR_NEEDPUBDIR + "to --build"
    ready, error = builddir_setup(config)
    if not ready:
        return error
    result = list()
    for x, source in enumerate(docs, 1):
        if not isinstance(source, SourceDocument):
            logger.info("%s (%d of %d) skipping, no source for orphan",
                        source.stem, x, len(docs))
            continue
        if not source.doctype:
            logger.warning("%s (%d of %d) skipping unknown doctype",
                           source.stem, x, len(docs))
            continue
        source.output = OutputDirectory.fromsource(config.pubdir, source)
        output = source.output
        runner = source.doctype(source=source, output=output, config=config)
        logger.info("%s (%d of %d) initiating build",
                    source.stem, x, len(docs))
        result.append(runner.generate())
    if all(result):
        return os.EX_OK
    for errcode, source in zip(result, docs):
        if not errcode:
            logger.error("%s build failed", source.stem)
    return "Build failed, see errors logged."


def script(config, docs, **kwargs):
    file = kwargs.get('file', sys.stdout)
    print(preamble, file=file)
    result = build(config, docs, **kwargs)
    print(postamble, file=file)
    return result


def publish(config, docs, **kwargs):
    config.build = True
    result = build(config, docs, **kwargs)
    if result != os.EX_OK:
        return result
    return os.EX_OK


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
    for cls in knowndoctypes:
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
        docs.add(SourceDocument(doc))
    return docs, remainder


def sameFilesystem(d0, d1):
    return os.stat(d0).st_dev == os.stat(d1).st_dev


def collectWorkset(config, args):
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

    # -- We only --list, --script, --build, or --publish on work-to-be-done
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
            return None, ERR_NEEDPUBDIR + "for inventory"
        if not config.sourcedir:
            return None, ERR_NEEDSOURCEDIR + "for inventory"
        inv = Inventory(config.pubdir, config.sourcedir)
        logger.info("Collected inventory containing %s documents.",
                    len(inv.all.keys()))
    else:
        inv = None

    if stati:
        oldsize = len(workset)
        for status in stati:
            collection = getattr(inv, status)
            workset.update(collection.values())
        growth = len(workset) - oldsize
        if growth:
            logger.info("Added %d docs, found by status class .", growth)

    unknownargs = None
    if remainder:
        docs, unknownargs = getDocumentsByStems(inv.all.values(), remainder)
        workset.update(docs)
        logger.info("Added %d docs, found by stem name.", len(docs))

    if unknownargs:
        return None, ERR_UNKNOWNARGS + ' '.join(unknownargs)

    # -- without any arguments (no files, no stems, no status_classes), the
    #    default behaviour is to either --build, --list or --script any
    #    available work, i.e. documents that have status new, orphan, broken,
    #    or stale.
    #
    if not workset:
        if not stati and not remainder:
            workset.update(inv.work.values())

    # -- and, of course, apply the skipping logic
    #
    workset, _ = processSkips(config, workset)

    docs = sorted(workset, key=lambda x: x.stem.lower())
    return docs, None


def handleArgs(config, args):

    if config.doctypes:
        return show_doctypes(config, *args)

    if config.statustypes:
        return show_statustypes(config, *args)

    if config.summary:
        return summary(config, *args)

    docs, error = collectWorkset(config, args)

    if error:
        return error

    if not docs:
        logger.info("No work to do.")
        return os.EX_OK

    if config.detail:
        return detail(config, docs)

    if config.script:
        return script(config, docs)

    if config.publish:
        return publish(config, docs)

    if not config.build:
        logger.info("Assuming --build, since no other action was specified...")
        config.build = True

    if config.build:
        return build(config, docs)

    return "Fell through handleArgs(); programming error."

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
    config, args = collectconfiguration(tag, argv)

    # -- and reset the loglevel (after reading envar, and config)
    #
    logging.getLogger().setLevel(config.loglevel)

    logger.debug("Received the following configuration:")
    for param, value in sorted(vars(config).items()):
        logger.debug("  %s = %r", param, value)
    logger.debug("  args: %r", args)

    return handleArgs(config, args)


def main():
    sys.exit(run(sys.argv[1:]))

if __name__ == '__main__':
    main()

#
# -- end of file
