#! /usr/bin/python
# -*- coding: utf8 -*-
#
# Copyright (c) 2016 Linux Documentation Project

from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import os
import time
import errno
import codecs
import hashlib
import subprocess
import functools
from functools import wraps
from tempfile import mkstemp, mkdtemp
import logging
logger = logging.getLogger(__name__)

opa = os.path.abspath
opb = os.path.basename
opd = os.path.dirname
opj = os.path.join

logdir = 'tldp-document-build-logs'


def logtimings(logmethod):
    def anon(f):
        @wraps(f)
        def timing(*args, **kwargs):
            s = time.time()
            result = f(*args, **kwargs)
            e = time.time()
            logmethod('running %s(%r, %r) took %.3f s',
                      f.__name__, args, kwargs, e - s)
            return result
        return timing
    return anon


def firstfoundfile(locations):
    '''return the first existing file from a list of filenames (or None)'''
    for option in locations:
        if isreadablefile(option):
            return option
    return None


def arg_isloglevel(l, defaultlevel=logging.ERROR):
    try:
        level = int(l)
        return level
    except ValueError:
        pass
    level = getattr(logging, l.upper(), None)
    if not level:
        level = defaultlevel
    return level


def arg_isstr(s):
    if isstr(s):
        return s
    return None


def arg_isreadablefile(f):
    if isreadablefile(f):
        return f
    return None


def arg_isdirectory(d):
    if os.path.isdir(d):
        return d
    return None


def arg_isexecutable(f):
    if isexecutable(f):
        return f
    return None


def sameFilesystem(d0, d1):
    return os.stat(d0).st_dev == os.stat(d1).st_dev


def stem_and_ext(name):
    '''return (stem, ext) for any relative or absolute filename'''
    return os.path.splitext(os.path.basename(os.path.normpath(name)))


def swapdirs(a, b):
    '''use os.rename() to make "a" become "b"'''
    if not os.path.isdir(a):
        raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), a)
    tname = None
    if os.path.exists(b):
        tdir = mkdtemp(prefix='swapdirs-', dir=opd(opa(a)))
        logger.debug("Created tempdir %s.", tdir)
        tname = opj(tdir, opb(b))
        logger.debug("About to rename %s to %s.", b, tname)
        os.rename(b, tname)
    logger.debug("About to rename %s to %s.", a, b)
    os.rename(a, b)
    if tname:
        logger.debug("About to rename %s to %s.", tname, a)
        os.rename(tname, a)
        logger.debug("About to remove %s.", tdir)
        os.rmdir(tdir)


def logfilecontents(logmethod, prefix, fname):
    '''log all lines of a file with a prefix '''
    with codecs.open(fname, encoding='utf-8') as f:
        for line in f:
            logmethod("%s: %s", prefix, line.rstrip())


def conditionallogging(result, prefix, fname):
    if logger.isEnabledFor(logging.DEBUG):
        logfilecontents(logger.debug, prefix, fname)  # -- always
    elif logger.isEnabledFor(logging.INFO):
        if result != 0:
            logfilecontents(logger.info, prefix, fname)  # -- error


def execute(cmd, stdin=None, stdout=None, stderr=None,
            logdir=None, env=os.environ):
    '''(yet another) wrapper around subprocess.Popen()

    The processing tools for handling DocBook SGML, DocBook XML and Linuxdoc
    all use different conventions for writing outputs.  Some write into the
    working directory.  Others write to STDOUT.  Others accept the output file
    as a required option.

    To allow for automation and flexibility, this wrapper function does what
    most other synchronous subprocess.Popen() wrappers does, but it adds a
    feature to record the STDOUT and STDERR of the executable.  This is
    helpful when trying to diagnose build failures of individual documents.

    Required:

      - cmd: (list form only; the paranoid prefer shell=False)
        this must include the whole command-line
      - logdir: an existing directory in which temporary log files
        will be created

    Optional:

      - stdin: if not supplied, STDIN (FD 0) will be left as is
      - stdout: if not supplied, STDOUT (FD 1) will be connected
        to a named file in the logdir (and left for later inspection)
      - stderr: if not supplied, STDERR (FD 2) will be connected
        to a named file in the logdir (and left for later inspection)
      - env: if not supplied, just use current environment

    Returns: the numeric exit code of the process

    Side effects:

      * will probably create temporary files in logdir
      * function calls wait(); process execution will intentionally block
        until the child process terminates

    Possible exceptions:

      * if the first element of list cmd does not contain an executable,
        this function will raise an AssertionError
      * if logdir is not a directory, this function will raise ValueError or
        IOError
      * and, of course, any exceptions passed up from calling subprocess.Popen

    '''
    prefix = os.path.basename(cmd[0]) + '.' + str(os.getpid()) + '-'

    assert isexecutable(cmd[0])

    if logdir is None:
        raise ValueError("logdir must be a directory, cannot be None.")

    if not os.path.isdir(logdir):
        raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), logdir)

    # -- not remapping STDIN, because that doesn't make sense here
    mytfile = functools.partial(mkstemp, prefix=prefix, dir=logdir)
    if stdout is None:
        stdout, stdoutname = mytfile(suffix='.stdout')
    else:
        stdoutname = None

    if stderr is None:
        stderr, stderrname = mytfile(suffix='.stderr')
    else:
        stderrname = None

    logger.debug("About to execute: %r", cmd)
    proc = subprocess.Popen(cmd, shell=False, close_fds=True,
                            stdin=stdin, stdout=stdout, stderr=stderr,
                            env=env, preexec_fn=os.setsid)
    result = proc.wait()
    if result != 0:
        logger.error("Non-zero exit (%s) for process: %r", result, cmd)
        logger.error("Find STDOUT/STDERR in %s/%s*", logdir, prefix)
    if isinstance(stdout, int) and stdoutname:
        os.close(stdout)
        conditionallogging(result, 'STDOUT', stdoutname)
    if isinstance(stderr, int) and stderrname:
        os.close(stderr)
        conditionallogging(result, 'STDERR', stderrname)
    return result


def isexecutable(f):
    '''True if argument is executable'''
    return os.path.isfile(f) and os.access(f, os.X_OK)


def isreadablefile(f):
    '''True if argument is readable file'''
    return os.path.isfile(f) and os.access(f, os.R_OK)


def isstr(s):
    '''True if argument is stringy (unicode or string)'''
    try:
        unicode
        stringy = (str, unicode)
    except NameError:
        stringy = (str,)  # -- python3
    return isinstance(s, stringy)


def which(program):
    '''return None or the full path to an executable (respecting $PATH)
http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/377028#377028
    '''
    fpath, fname = os.path.split(program)
    if fpath and isexecutable(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            sut = os.path.join(path, program)
            if isexecutable(sut):
                return sut
    return None


def writemd5sums(fname, md5s, header=None):
    '''write an MD5SUM file from [(filename, MD5), ...]'''
    with codecs.open(fname, 'w', encoding='utf-8') as file:
        if header:
            print(header, file=file)
        for fname, hashval in sorted(md5s.items()):
            print(hashval + '  ' + fname, file=file)


def md5file(name):
    '''return MD5 hash for a single file name'''
    with open(name, 'rb') as f:
        bs = f.read()
    md5 = hashlib.md5(bs).hexdigest()
    try:
        md5 = unicode(md5)
    except NameError:
        pass  # -- python3
    return md5


def statfile(name):
    '''return posix.stat_result (or None) for a single file name'''
    try:
        st = os.lstat(name)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise e
        st = None
    return st


def md5files(name, relative=None):
    '''get all of the MD5s for files from here downtree'''
    return fileinfo(name, relative=relative, func=md5file)


def statfiles(name, relative=None):
    '''
    >>> statfiles('./docs/x509').keys()
    ['./docs/x509/tutorial.rst', './docs/x509/reference.rst', './docs/x509/index.rst']
    >>> statfiles('./docs/x509', relative='./').keys()
    ['docs/x509/reference.rst', 'docs/x509/tutorial.rst', 'docs/x509/index.rst']
    >>> statfiles('./docs/x509', relative='./docs/x509/').keys()
    ['index.rst', 'tutorial.rst', 'reference.rst']
    '''
    return fileinfo(name, relative=relative, func=statfile)


def fileinfo(name, relative=None, func=statfile):
    '''return a dict() with keys being filenames and posix.stat_result values

    Required:

      name: the name should be an existing file, but accessing filesystems
            can be a racy proposition, so if the name is ENOENT, returns an
            empty dict()
            if name is a directory, os.walk() over the entire subtree and
            record and return all stat() results

    Optional:

      relative: if the filenames in the keys should be relative some other
                directory, then supply that path here (see examples)


    Bugs:
      Dealing with filesystems is always potentially a racy affair.  They go
      out for lunch sometimes.  They don't call.  They don't write.  But, at
      least we can try to rely on them as best we can--mostly, by just
      excluding any files (in the output dict()) which did not return a valid
      posix.stat_result.
    '''
    info = dict()
    if not os.path.exists(name):
        return info
    if not os.path.isdir(name):
        if relative:
            relpath = os.path.relpath(name, start=relative)
        else:
            relpath = name
        info[relpath] = func(name)
        if info[relpath] is None:
            del info[relpath]
    else:
        for root, dirs, files in os.walk(name):
            inodes = list()
            inodes.extend(dirs)
            inodes.extend(files)
            for x in inodes:
                foundpath = os.path.join(root, x)
                if os.path.isdir(foundpath):
                    continue
                if relative:
                    relpath = os.path.relpath(foundpath, start=relative)
                else:
                    relpath = foundpath
                info[relpath] = func(foundpath)
                if info[relpath] is None:
                    del info[relpath]
    return info

#
# -- end of file
