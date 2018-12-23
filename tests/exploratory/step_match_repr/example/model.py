# -*- coding: utf-8 -*-


class Hero(object):
    def __init__(self, forename, surname, hero):
        self.forename = forename
        self.surname = surname
        self.heroname = hero

    def __repr__(self):
        return "Hero({0}, {1}, {2})".format(self.forename, self.surname, self.heroname)
