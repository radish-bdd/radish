class Hero:
    def __init__(self, forename, surname, hero):
        self.forename = forename
        self.surname = surname
        self.heroname = hero

    def __repr__(self):
        return "Hero({}, {}, {})".format(self.forename, self.surname, self.heroname)
