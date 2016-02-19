#! /usr/bin/python
# -*- coding: utf8 -*-

from __future__ import absolute_import, division, print_function

import os
import io
import sys
import errno
import operator
import subprocess
import functools
from tempfile import mkstemp
import logging

logdir = 'tldp-document-build-logs'


def getLogger(**opts):
    level = opts.get('level', logging.INFO)
    logging.basicConfig(stream=sys.stderr, level=level)
    logger = logging.getLogger()
    return logger

logger = getLogger()


def stem_and_ext(name):
    '''return (stem, ext) for any relative or absolute filename'''
    return os.path.splitext(os.path.basename(os.path.normpath(name)))


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
    if stdout is None:
        stdout, stdoutname = mkstemp(prefix=prefix, suffix='.stdout',
                                     dir=logdir)
    if stderr is None:
        stderr, stderrname = mkstemp(prefix=prefix, suffix='.stderr',
                                     dir=logdir)

    logger.debug("About to execute: %r", cmd)
    proc = subprocess.Popen(cmd, shell=False, close_fds=True,
                            stdin=stdin, stdout=stdout, stderr=stderr,
                            env=env, preexec_fn=os.setsid)
    result = proc.wait()
    if result != 0:
        logger.warning("Return code (%s) for process: %r", result, cmd)
        logger.warning("Find STDOUT/STDERR in %s/%s", logdir, prefix)
    return result


def isexecutable(fpath):
    '''True if argument is executable'''
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


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


def makefh(thing):
    '''return a file object; given an existing filename name or file object'''
    if isinstance(thing, io.IOBase):
        f = thing
    elif isinstance(thing, str) and os.path.isfile(thing):
        f = open(thing)
    else:
        raise TypeError("Cannot make file from %s of %r" %
                        (type(thing), thing,))
    return f


def statfile(name):
    '''return posix.stat_result (or None) for a single file name'''
    try:
        st = os.stat(name)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise e
        if os.path.islink(name):
            st = os.lstat(name)
        else:
            st = None
    return st


def statfiles(name, relative=None):
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

    Examples:

    >>> statfiles('./docs/x509').keys()
    ['./docs/x509/tutorial.rst', './docs/x509/reference.rst', './docs/x509/index.rst']
    >>> statfiles('./docs/x509', relative='./').keys()
    ['docs/x509/reference.rst', 'docs/x509/tutorial.rst', 'docs/x509/index.rst']
    >>> statfiles('./docs/x509', relative='./docs/x509/').keys()
    ['index.rst', 'tutorial.rst', 'reference.rst']
    '''
    statinfo = dict()
    if not os.path.exists(name):
        return statinfo
    if not os.path.isdir(name):
        if relative:
            relpath = os.path.relpath(name, start=relative)
        else:
            relpath = name
        statinfo[relpath] = statfile(name)
        if statinfo[relpath] is None:
            del statinfo[relpath]
    else:
        for root, dirs, files in os.walk(name):
            inodes = list()
            inodes.extend(dirs)
            inodes.extend(files)
            for x in inodes:
                foundpath = os.path.join(root, x)
                if relative:
                    relpath = os.path.relpath(foundpath, start=relative)
                else:
                    relpath = foundpath
                statinfo[relpath] = statfile(foundpath)
                if statinfo[relpath] is None:
                    del statinfo[relpath]
    return statinfo


def att_statinfo(statinfo, attr='st_mtime', func=max):
    if statinfo:
        return func([getattr(v, attr) for v in statinfo.values()])
    else:
        return 0


max_size = functools.partial(att_statinfo, attr='st_size', func=max)
min_size = functools.partial(att_statinfo, attr='st_size', func=min)

max_mtime = functools.partial(att_statinfo, attr='st_mtime', func=max)
min_mtime = functools.partial(att_statinfo, attr='st_mtime', func=min)

max_ctime = functools.partial(att_statinfo, attr='st_ctime', func=max)
min_ctime = functools.partial(att_statinfo, attr='st_ctime', func=min)

max_atime = functools.partial(att_statinfo, attr='st_atime', func=max)
min_atime = functools.partial(att_statinfo, attr='st_atime', func=min)


def sieve(operand, statinfo, attr='st_mtime', func=operator.gt):
    result = set()
    for fname, stbuf in statinfo.items():
        if func(getattr(stbuf, attr), operand):
            result.add(fname)
    return result

mtime_gt = functools.partial(sieve, attr='st_mtime', func=operator.gt)
mtime_lt = functools.partial(sieve, attr='st_mtime', func=operator.lt)

size_gt = functools.partial(sieve, attr='st_size', func=operator.gt)
size_lt = functools.partial(sieve, attr='st_size', func=operator.lt)

#
# -- end of file
