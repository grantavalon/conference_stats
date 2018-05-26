import requests
import re
from bs4 import BeautifulSoup, Comment
import pandas as pd
import string


def get_letters(ignore=('x', )):
	"""
	Gets a list of English letters

	:param ignore: (tuple) Letters to ignore
	:return: (list)
	"""
    letters = list(string.ascii_lowercase)
    for letter in ignore:
        letters.remove(letter)
    return letters


def get_all_players():
	"""
	Gets bkref ids of all players who have ever played in the league

	:return: (list)
	"""
    letters = get_letters()
    all_players = []
    for letter in letters:
        directory = 'https://www.basketball-reference.com/players/{}/index.html'.format(letter)
        html = requests.get(directory).content
        ids = re.findall('data-append-csv="(.+?)" data-stat="player"', html)
        all_players.extend(ids)
    return all_players


def get_player_conference(html):
	"""
	Gets the last collegiate conference of a player

	:param html: (str) the html of a player's bkref page
	:return: (str or None)
	"""
    college_urls = re.findall('<a href="(.+?)">College Basketball at Sports-Reference.com', html)
    if len(college_urls) > 0:
        try:
            html = requests.get(college_urls[0]).content
            soup = BeautifulSoup(html, 'lxml')
            table = soup.find_all('table', {'class': 'row_summable sortable stats_table'})[0]
            conference = re.findall('/cbb/conferences/(.+)/\d{4}.html">', str(table))[-1]
            return conference
        except:
            pass


def get_one_player_career_totals(player_id):
	"""
	Gets the table of career totals for a given player, along with collegiate conference

	:param player_id: (str) bkref id for a player
	:return: (DataFrame)
	"""
    url = 'https://www.basketball-reference.com/players/{}/{}.html'.format(player_id[0], player_id)
    html = requests.get(url).content
    soup = BeautifulSoup(html, 'lxml')
    comments = soup.find_all(string=lambda text:isinstance(text,Comment))
    table = next((comment for comment in comments if 'id="totals"' in comment), None)
    df = pd.read_html(str(table))[0].dropna(axis=1).drop_duplicates('Season')
    df['conference'] = get_player_conference(html)
    df['player_id'] = player_id
    return df 


def create_dataset():
	"""
	Creates the dataset of all player season-by-season totals and their collegiate conferences

	:return:
	"""
	dataset = pd.DataFrame()
	players = get_all_players()
	for player in players:
		print player
		player_career_totals = get_one_player_career_totals(player)
		dataset = dataset.append(player_career_totals)
	dataset.to_csv('player_dataset.csv')


if __name__ == "__main__":
	create_dataset()





