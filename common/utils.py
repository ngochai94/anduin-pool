import csv, itertools, math, trueskill, matplotlib
import seaborn as sns, pandas as pd, matplotlib.pyplot as plt
from common.tournament import Tournament
from common.match import Match
from common.player import Player


def load_match_data(path='data/result.csv'):
    res = []
    with open(path) as file:
        reader = csv.reader(file)
        for row in itertools.islice(reader, 1, None):
            season, win1, win2, lose1, lose2, tier = row
            res.append(Match(int(season), win1, win2, lose1, lose2, tier))
    return res

def init_tournament(path='data/result.csv'):
    return Tournament(load_match_data(path))

def _get_player_rating(tournament):
    seasons = [0] + list(tournament.seasons.keys())
    sorted_players = sorted(tournament.players.items(), 
                            key=lambda x:x[1].rating.exposure, reverse=True)
    player_ratings = {name: player.get_seasons_exposure(seasons) 
                      for name, player in sorted_players}
    return seasons, player_ratings

def draw_rating_change(tournament):
    seasons, player_ratings = _get_player_rating(tournament)
    data = pd.melt(pd.DataFrame({**player_ratings, **{'Season': seasons}}), ['Season'],
                var_name='Player', value_name='Rating')
    sns.set(rc={'figure.figsize':(15, 10)}, palette='bright', style='darkgrid')
    sns.lineplot(x='Season', y='Rating', hue='Player', data=data)
    return pd.DataFrame(player_ratings).fillna(0.0).astype(int).transpose()

def draw_ranking_change(tournament):
    seasons, player_ratings = _get_player_rating(tournament)
    player_rankings = pd.DataFrame(player_ratings).rank(1, ascending=False, method='first')
    data = pd.melt(pd.DataFrame({**player_rankings, **{'Season': seasons}}), ['Season'],
                var_name='Player', value_name='Rating')
    sns.set(rc={'figure.figsize':(17, 7)})
    fig = sns.lineplot(x='Season', y='Rating', hue='Player', data=data)
    fig.invert_yaxis()
    return player_rankings.transpose().applymap(lambda x: '-' if math.isnan(x) else int(x))

def get_match_prob(tournament):
    df = pd.DataFrame(sorted([{
        'Winner team': f'{match.win1} + {match.win2}',
        'Loser team': f'{match.lose1} + {match.lose2}',
        'Season': match.season,
        'Probability': tournament.get_match_probability(match)
    } for match in tournament.matches], key=lambda match: match['Probability']))
    df['Probability'] = df['Probability'].map(lambda prob: f'{prob * 100:.1f}%')
    return df

def _get_player_summary(tournament):
    summary = tournament.get_players_summary()
    df = pd.DataFrame([{
        'name': name,
        'sf': s.sf_win + s.sf_lose,
        'wf': s.wf_win + s.wf_lose,
        'lf': s.lf_win + s.lf_lose,
        'sf_winrate': s.sf_win * 100 / max(1, s.sf_win + s.sf_lose),
        'wf_winrate': s.wf_win * 100 / max(1, s.wf_win + s.wf_lose),
        'lf_winrate': s.lf_win * 100 / max(1, s.lf_win + s.lf_lose),
        'total': s.sf_win + s.wf_win + s.lf_win + s.sf_lose + s.wf_lose + s.lf_lose,
        'total_winrate': (s.sf_win + s.wf_win + s.lf_win) * 100 / max(1, s.sf_win + 
                    s.wf_win + s.lf_win + s.sf_lose + s.wf_lose + s.lf_lose)
    } for name, s in summary.items()])
    return df

def _draw_tier_summary(tournament, tier, title):
    summary = _get_player_summary(tournament)
    tier_winrate = tier + '_winrate'
    data = summary.loc[summary[tier] > 0].sort_values(by=[tier_winrate, tier], ascending=False)

    fig, ax1 = plt.subplots(figsize=(7,4))
    ax1.set_title(title, fontsize=16)
    ax2 = ax1.twinx()

    sns.barplot(x='name', y=tier, data=data, ax=ax1, palette='GnBu_r')
    sns.lineplot(x='name', y=tier_winrate, data=data,
                sort=False, marker='o', ax=ax2, color='red')

    ax1.set_xlabel('')
    ax1.set_ylabel('Match played', color='blue')
    ax2.set_ylabel('Winrate %', color='red')
    ax2.set_yticks(range(0, 110, 10))

def draw_wf_summary(tournament):
    _draw_tier_summary(tournament, 'wf', 'Winner final')

def draw_lf_summary(tournament):
    _draw_tier_summary(tournament, 'lf', 'Loser final')

def draw_sf_summary(tournament):
    _draw_tier_summary(tournament, 'sf', 'Semi-final')

def draw_overall_summary(tournament):
    _draw_tier_summary(tournament, 'total', 'Overall')

def draw_team_summary(tournament):
    summary = tournament.get_teams_summary()
    df = pd.DataFrame(summary.values())
    df['total'] = df.w + df.l
    df = df.sort_values(by=['total', 'w'], ascending=False)
    _, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(x='name', y='total', data=df, label='Lost', color='r')
    plot = sns.barplot(x='name', y='w', data=df, label='Win', color='g')

    ax.legend()
    ax.set(ylabel='')
    plt.setp(plot.get_xticklabels(), rotation=45, horizontalalignment='right')
