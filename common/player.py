class Player:
    def __init__(self, name, rating, pre=0):
        self.name = name
        self.rating = rating
        self.past_rating = {pre: rating}

    def participated_in_season(self, season):
        return season in self.past_rating

    def get_season_rating(self, season):
        return self.past_rating[season] if self.participated_in_season(season) else None

    def set_rating(self, rating):
        self.rating = rating

    def set_season_rating(self, season, rating):
        self.past_rating[season] = rating
        self.rating = rating

    def lock_season_rating(self, season):
        self.past_rating[season] = self.rating

    def get_seasons_exposure(self, seasons):
        return [self.past_rating[season].exposure if self.participated_in_season(season) else None for season in seasons]

class PlayerSummary:
    def __init__(self, sf_win=0, wf_win=0, lf_win=0, sf_lose=0, wf_lose=0, lf_lose=0):
        self.sf_win = sf_win
        self.wf_win = wf_win
        self.lf_win = lf_win
        self.sf_lose = sf_lose
        self.wf_lose = wf_lose
        self.lf_lose = lf_lose

    def update_win(self, tier):
        if tier == 'sf':
            self.sf_win += 1
        elif tier == 'lf':
            self.lf_win += 1
        elif tier == 'wf':
            self.wf_win += 1
    def update_lose(self, tier):
        if tier == 'sf':
            self.sf_lose += 1
        elif tier == 'lf':
            self.lf_lose += 1
        elif tier == 'wf':
            self.wf_lose += 1
