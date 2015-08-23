# -*- coding: utf-8 -*-

__author__ = 'Alexey'

class cPlan(object):
    """
    An easy way to build and maintain budget-like information
    """
    def __init__(self):
        self.plans = {}
        self.is_sorted = 0
        self.active_whens = []
        self.active_whats = []

    def add_plan(self, pl_when, pl_what, pl_howmuch):
        if not(pl_when in self.plans):
            self.plans[pl_when] = {}
            self.active_whens += [pl_when]
            self.is_sorted = 0
        if not(pl_what in self.plans[pl_when]):
            self.plans[pl_when][pl_what] = 0
            if pl_what not in self.active_whats:
                self.active_whats += [pl_what]
        self.plans[pl_when][pl_what] += pl_howmuch

    def get_avail_whats(self):
        return self.active_whats

    def get_howmuch_between_whens(self, what, when1, when2):
        if when1 > when2:
            raise BaseException('cPlan.get_whats_between_whens(when1, when2) - should be when1<=when2 !')
        if not what in self.active_whats:
            return 0
        N = len(self.active_whens)
        if N==0:
            return 0
        if not self.is_sorted:
            self.active_whens.sort()
            self.is_sorted = 1
        min_when = self.active_whens[0]
        max_when = self.active_whens[N-1]
        if when1 > max_when:
            return 0
        if when2 < min_when:
            return 0

        c = 0
        t = self.active_whens[c]
        howmuch = 0
        while t <= when2 and c <= N-1:
            t = self.active_whens[c]
            if t >= when1:
                if what in self.plans[t]:
                    howmuch += self.plans[t][what]
            c += 1
        return howmuch

    def close_nearest_plan(self, what, howmuch):
        # find last ones with this whats
        N = len(self.active_whens)
        if N==0:
            return
        if not self.is_sorted:
            self.active_whens.sort()
            self.is_sorted = 1
        c = 0
        left_to_close = howmuch
        while left_to_close > 0 and c <= N-1:
            t = self.active_whens[c]
            if what in self.plans[t]:
                if self.plans[t][what] < left_to_close:
                    left_to_close -= self.plans[t][what]
                    self.plans[t][what] = 0
                else:
                    self.plans[t][what] -= left_to_close
                    left_to_close = 0
            c += 1

    def wipe(self):
        self.plans = {}
        self.is_sorted = 0
        self.active_whens = []
        self.active_whats = []

    def forget_history(self, last_when):
        # clean the memory, speedup lookups
        N = len(self.active_whens)
        if N==0:
            return
        if not self.is_sorted:
            self.active_whens.sort()
            self.is_sorted = 1
        min_when = self.active_whens[0]
        max_when = self.active_whens[N-1]
        if min_when >= last_when:
            # no need to forget
            return
        if max_when < last_when:
            # our plan is completely outdated
            self.wipe()
            return

        c = 0
        t = self.active_whens[c]
        while t < last_when and c <= N-1:
            t = self.active_whens[c]
            forget_it = self.plans.pop(t)
            forget_it = None # hopefully it'll work better this way
            c += 1
