#! /usr/bin/python
# -*- coding: utf8 -*-
#
# Copyright (c) 2016 Linux Documentation Project

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import os
import sys
import errno
import signal
import shutil
import logging
import inspect
import collections
from argparse import Namespace

from tldp.typeguesser import knowndoctypes
from tldp.sources import SourceDocument, arg_issourcedoc
from tldp.outputs import OutputDirectory
from tldp.inventory import Inventory, status_classes, status_types, stypes
from tldp.config import collectconfiguration
from tldp.utils import arg_isloglevel, arg_isdirectory
from tldp.utils import swapdirs, sameFilesystem
from tldp.doctypes.common import preamble, postamble

# -- Don't freak out with IOError when our STDOUT, handled with
#    head, sed, awk, grep, etc; and, also deal with a user's ctrl-C
#    the same way (i.e. no traceback, just stop)
#
signal.signal(signal.SIGPIPE, signal.SIG_DFL)
signal.signal(signal.SIGINT, signal.SIG_DFL)

logformat = '%(levelname)-9s %(name)s %(filename)s#%(lineno)s ' \
    + '%(funcName)s %(message)s'
logging.basicConfig(stream=sys.stderr, format=logformat, level=logging.ERROR)
logger = logging.getLogger(__name__)

# -- short names
#
opa = os.path.abspath
opb = os.path.basename
opd = os.path.dirname
opj = os.path.join

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
    print('', file=file)
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
        print('', file=file)
    print('', file=file)
    return os.EX_OK


def show_statustypes(config, *args, **kwargs):
    if args:
        return ERR_EXTRAARGS + ' '.join(args)
    file = kwargs.get('file', sys.stdout)
    width = 2 + max([len(x) for x in status_types])
    print("Basic status types:", file=file)
    print('', file=file)
    for status, descrip in stypes.items():
        fmt = '{status:>{width}}:  {descrip}'
        text = fmt.format(status=status, descrip=descrip, width=width)
        print(text, file=file)
    print('', file=file)
    print("Synonyms and groups:", file=file)
    print('', file=file)
    for status, descrip in status_classes.items():
        fmt = '{status:>{width}}:  {descrip}'
        descrip = ', '.join(descrip)
        text = fmt.format(status=status, descrip=descrip, width=width)
        print(text, file=file)
    print('', file=file)
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
    width.doctype = max([len(x.__name__) for x in knowndoctypes])
    width.status = max([len(x) for x in status_types])
    width.count = len(str(len(inv.source.keys())))
    print('By Document Status (STATUS)', '---------------------------',
          sep='\n', file=file)
    for status in status_types:
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
    print('', 'By Document Type (DOCTYPE)', '--------------------------',
          sep='\n', file=file)
    summarybytype = collections.defaultdict(list)
    for doc in inv.source.values():
        name = doc.doctype.__name__
        summarybytype[name].append(doc.stem)
    for doctype, docs in summarybytype.items():
        count = len(docs)
        s = '{0:{w.doctype}}  {1:{w.count}}  '.format(doctype, count, w=width)
        print(s, end="", file=file)
        if config.verbose:
            print(', '.join(docs), file=file)
        else:
            abbrev = docs
            s = ''
            if abbrev:
                s = s + abbrev.pop(0)
                while abbrev:
                    if (len(s) + len(abbrev[0])) > 36:
                        break
                    s = s + ', ' + abbrev.pop(0)
                if abbrev:
                    s = s + ', and %d more ...' % (len(abbrev))
            print(s, file=file)
    print('', file=file)
    return os.EX_OK


def detail(config, docs, **kwargs):
    file = kwargs.get('file', sys.stdout)
    width = Namespace()
    width.doctype = max([len(x.__name__) for x in knowndoctypes])
    width.status = max([len(x) for x in status_types])
    width.stem = max([len(x.stem) for x in docs])
    # -- if user just said "list" with no args, then give the user something
    #    sane, "all"; it would make sense for this to be "work", too, but
    #    "all" seems to be less surprising
    #
    for doc in docs:
        doc.detail(width, config.verbose, file=file)
    return os.EX_OK


def removeOrphans(docs):
    sources = list()
    for x, doc in enumerate(docs, 1):
        if not isinstance(doc, SourceDocument):
            logger.info("%s (%d of %d) removing:  no source for orphan",
                        doc.stem, x, len(docs))
            continue
        sources.append(doc)
    return sources


def removeUnknownDoctypes(docs):
    sources = list()
    for x, doc in enumerate(docs, 1):
        if not doc.doctype:
            logger.info("%s (%d of %d) removing:  unknown doctype",
                        doc.stem, x, len(docs))
            continue
        sources.append(doc)
    return sources


def createBuildDirectory(d):
    if not arg_isdirectory(d):
        logger.debug("Creating build directory %s.", d)
        try:
            os.mkdir(d)
        except OSError as e:
            logger.critical("Could not make --builddir %s.", d)
            return False, e.errno
    return True, d


def builddir_setup(config):
    '''create --builddir; ensure it shares a filesystem with --pubdir'''
    if not config.builddir:
        builddir = opj(opd(opa(config.pubdir)), 'ldptool-build')
        ready, error = createBuildDirectory(builddir)
        if not ready:
            return ready, error
        config.builddir = builddir

    if not sameFilesystem(config.pubdir, config.builddir):
        return False, "--pubdir and --builddir must be on the same filesystem"

    return True, None


def create_dtworkingdir(config, docs):
    for source in docs:
        classname = source.doctype.__name__
        source.dtworkingdir = opj(config.builddir, classname)
        ready, error = createBuildDirectory(source.dtworkingdir)
        if not ready:
            return ready, error
    return True, None


def post_publish_cleanup(workingdirs):
    '''clean up empty directories left under --builddir'''
    for d in workingdirs:
        if os.path.isdir(d):
            try:
                logger.debug("removing build dir %s", d)
                os.rmdir(d)
            except OSError as e:
                if e.errno != errno.ENOTEMPTY:
                    raise
                logger.debug("Could not remove %s; files still present", d)


def prepare_docs_script_mode(config, docs):
    for source in docs:
        if not source.output:
            fromsource = OutputDirectory.fromsource
            if not config.pubdir:
                source.working = fromsource(source.dirname, source)
            else:
                source.working = fromsource(config.pubdir, source)
        else:
            source.working = source.output
    return True, None


def prepare_docs_build_mode(config, docs):
    ready, error = create_dtworkingdir(config, docs)
    if not ready:
        return ready, error
    for source in docs:
        d = source.dtworkingdir
        source.working = OutputDirectory.fromsource(d, source)
        if not source.output:
            source.output = OutputDirectory.fromsource(config.pubdir, source)
    return True, None


def docbuild(config, docs, **kwargs):
    buildsuccess = False
    result = list()
    for x, source in enumerate(docs, 1):
        working = source.working
        runner = source.doctype(source=source, output=working, config=config)
        status = 'progress, %d failures, %d successes'
        status = status % (result.count(False), result.count(True),)
        logger.info("%s (%d of %d) initiating build [%s]",
                    source.stem, x, len(docs), status)
        result.append(runner.generate(**kwargs))
    if all(result):
        buildsuccess = True
    return buildsuccess, list(zip(result, docs))


def script(config, docs, **kwargs):
    ready, error = prepare_docs_script_mode(config, docs)
    if not ready:
        return error
    file = kwargs.get('file', sys.stdout)
    print(preamble, file=file)
    buildsuccess, results = docbuild(config, docs, **kwargs)
    print(postamble, file=file)
    for errcode, source in results:
        if not errcode:
            logger.error("Could not generate script for %s", source.stem)
    if buildsuccess:
        return os.EX_OK
    else:
        return "Script generation failed."


def build(config, docs, **kwargs):
    if not config.pubdir:
        return ERR_NEEDPUBDIR + "to --build"
    ready, error = builddir_setup(config)
    if not ready:
        return error
    ready, error = prepare_docs_build_mode(config, docs)
    if not ready:
        return error
    buildsuccess, results = docbuild(config, docs, **kwargs)
    for x, (buildcode, source) in enumerate(results, 1):
        if buildcode:
            logger.info("success (%d of %d) available in %s",
                        x, len(results), source.working.dirname)
        else:
            logger.info("FAILURE (%d of %d) available in %s",
                        x, len(results), source.working.dirname)
    if buildsuccess:
        return os.EX_OK
    else:
        return "Build failed, see logging output in %s." % (config.builddir,)


def publish(config, docs, **kwargs):
    config.build = True
    result = build(config, docs, **kwargs)
    if result != os.EX_OK:
        return result
    for x, source in enumerate(docs, 1):
        logger.info("Publishing (%d of %d) to %s.",
                    x, len(docs), source.output.dirname)
        # -- swapdirs must raise an error if there are problems
        #
        swapdirs(source.working.dirname, source.output.dirname)
        if os.path.isdir(source.working.dirname):
            logger.debug("%s removing old directory %s",
                         source.stem, source.working.dirname)
            shutil.rmtree(source.working.dirname)
    workingdirs = list(set([x.dtworkingdir for x in docs]))
    workingdirs.append(config.builddir)
    post_publish_cleanup(workingdirs)
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
        logger.info("Inventory contains %s source and %s output documents.",
                    len(inv.source.keys()), len(inv.output.keys()))
    else:
        inv = None

    if stati:
        docs = getDocumentsByStatus(inv.all.values(), stati)
        workset.update(docs)
        if docs:
            logger.info("Added %d docs, found by status class .", len(docs))

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

    # -- build(), script() and publish() will not be able to deal
    #    with orphans or with unknown source document types
    #
    docs = removeUnknownDoctypes(removeOrphans(docs))

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
