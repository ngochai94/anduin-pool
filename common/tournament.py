import itertools, math
from common.player import Player, PlayerSummary
from trueskill import rate, Rating, TrueSkill
from itertools import groupby

class Tournament:

    BASE = 2000
    SIGMA = 200
    BETA = SIGMA / 2
    TAU = SIGMA / 100

    def _get_player_by_name(self, name, season):
        if name not in self.players:
            self.players[name] = Player(name, Rating(self.BASE, self.SIGMA), season - 1)
        return self.players[name]

    def _update_rating_post_match(self, match):
        player1 = self._get_player_by_name(match.win1, match.season)
        player2 = self._get_player_by_name(match.win2, match.season)
        player3 = self._get_player_by_name(match.lose1, match.season)
        player4 = self._get_player_by_name(match.lose2, match.season)
        team1 = [player1.rating, player2.rating]
        team2 = [player3.rating, player4.rating]
        [(rating1, rating2), (rating3, rating4)] =  rate([team1, team2])
        player1.set_rating(rating1)
        player2.set_rating(rating2)
        player3.set_rating(rating3)
        player4.set_rating(rating4)

    def _update_rating_post_season(self, season, matches):
        [self._update_rating_post_match(match) for match in matches]
        [player.lock_season_rating(season) for player in self.players.values()]

    def __init__(self, matches):
        self.players = {}
        self.matches = matches
        self.seasons = {k: list(v) for k, v in groupby(matches, lambda match:match.season)}
        [self._update_rating_post_season(season, matches) for season, matches in self.seasons.items()]

    def get_season_ranking(self, season):
        players_and_rating = sorted([
            (player.name, player.get_season_rating(season))
            for player in self.players.values()
            if player.participated_in_season(season)
        ], key=lambda x:x[1].exposure, reverse=True)
        return players_and_rating

    def get_current_ranking(self):
        players_and_rating = sorted([
            (player.name, player.rating)
            for player in self.players.values()
        ], key=lambda x:x[1].exposure, reverse=True)
        return players_and_rating

    def get_player_rating_before_season(self, name, season):
        return self.players[name].get_season_rating(season - 1)

    def win_probability(self, team1, team2):
        delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
        sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
        size = len(team1) + len(team2)
        denom = math.sqrt(size * (self.BETA * self.BETA) + sum_sigma)
        ts = TrueSkill(self.BASE, self.SIGMA, self.BETA, self.TAU, 0)
        return ts.cdf(delta_mu / denom)

    def get_match_probability(self, match):
        team1 = [
            self.get_player_rating_before_season(match.win1, match.season),
            self.get_player_rating_before_season(match.win2, match.season)
        ]
        team2 = [
            self.get_player_rating_before_season(match.lose1, match.season),
            self.get_player_rating_before_season(match.lose2, match.season)
        ]
        return self.win_probability(team1, team2)

    def get_player_win_rate(self, name):
        win = lose = 0
        for match in self.matches:
            if name in [match.win1, match.win2]:
                win += 1
            elif name in [match.lose1, match.lose2]:
                lose += 1
        return win / (win + lose)

    def get_players_summary(self):
        summary = {name: PlayerSummary() for name in self.players.keys()}
        for match in self.matches:
            summary[match.win1].update_win(match.tier)
            summary[match.win2].update_win(match.tier)
            summary[match.lose1].update_lose(match.tier)
            summary[match.lose2].update_lose(match.tier)
        return summary

    def get_teams_summary(self):
        summary = {}
        def update(player1, player2, result):
            team = ' + '.join(sorted([player1, player2]))
            if team not in summary:
                summary[team] = {'w': 0, 'l': 0, 'name': team}
            summary[team][result] += 1
        for match in self.matches:
            update(match.win1, match.win2, 'w')
            update(match.lose1, match.lose2, 'l')
        return summary
