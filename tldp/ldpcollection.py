#! /usr/bin/python
# -*- coding: utf8 -*-
#
# Copyright (c) 2016 Linux Documentation Project

from __future__ import absolute_import, division, print_function

import collections


class LDPDocumentCollection(collections.MutableMapping):
    '''a dict-like container for DocumentCollection objects

    Intended to be subclassed.

    Implements all the usual dictionary stuff, but also provides sorted
    lists of documents in the collection.
    '''
    def __repr__(self):
        return '<%s:(%s docs)>' % (self.__class__.__name__, len(self))

    def __delitem__(self, key):
        del self.__dict__[key]

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def iterkeys(self):
        return iter(self.keys)

    def itervalues(self):
        for key in sorted(self, key=lambda x: x.lower()):
            yield self[key]

    def iteritems(self):
        for key in self.keys:
            yield (key, self[key])

    def keys(self):
        return sorted(self, key=lambda x: x.lower())

    def items(self):
        return [(key, self[key]) for key in self.keys()]

    def values(self):
        return [self[key] for key in self.keys()]

#
# -- end of file
