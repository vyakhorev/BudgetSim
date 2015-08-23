# -*- coding: utf-8 -*-

__author__ = 'Alexey'

class abst_key(object):
    def __repr__(self):
        return self.string_key()

    def _my_key(self):
        # You may re-implement this
        if hasattr(self, 'name'):
            return (self.name, id(self))
        else:
            return (id(self))

    def string_key(self):
        s_r = ""
        for s in self._my_key():
            s_r += str(s)
        return s_r

    def __eq__(x, y):
        return x._my_key() == y._my_key()

    def __hash__(self):
        return hash(self._my_key())
