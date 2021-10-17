class Match:
    def __init__(self, season, win1, win2, lose1, lose2, tier):
        self.season = season
        self.win1 = win1
        self.win2 = win2
        self.lose1 = lose1
        self.lose2 = lose2
        self.tier = tier

    def get_participants(self):
        return [self.win1, self.win2, self.lose1, self.lose2]
