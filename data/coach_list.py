import requests
import re
import time
import csv
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from helpers import *

"""
This script uses coaching data to scrape team-level data such as home team info over 
all games in the DB.
"""
def main():
  
  wfile = open("coach_data.csv", "wb")
  field_names = ['game_id','coach_id', 'team', 'is_home', 'year']
  writer = csv.writer(wfile)
  writer.writerow(field_names) 
  coach_dict = get_coach_dict()
  games_data = pd.read_csv('games-data2.csv')
  game_ids = np.unique(np.array(games_data['game_id']))
  early_months = ['January', 'February', 'March']
  count = 1
  for id in game_ids:
    game_url = 'http://scores.espn.go.com/nfl/boxscore?gameId=%s' % (id)
    game_res = requests.get(game_url)
    soup = BeautifulSoup(game_res.content)
    
    #away team extraction
    away_div = soup.find('div', class_="team away")   
    href_away = away_div.find_all('a')
    href_str_away = str(href_away)
    away_team = re.search(r'/name/(\w+)/([\w.\'-]+-[\w\']+)', href_str_away)
    away_team_name = away_team.group(1)
    #home team extraction
    home_div = soup.find('div', class_="team home")
    href_home = home_div.find_all('a')
    href_str_home = str(href_home)
    home_team = re.search(r'/name/(\w+)/([\w.\'-]+-[\w\']+)', href_str_home)
    home_team_name = home_team.group(1)

    time_div = soup.find('div', class_="game-time-location")
    date_p = str(time_div.find('p').contents[0])
    date = re.search(r'ET,\s(\w+)\s\w+,\s(\d+)', date_p)
    month = date.group(1)
    year = int(date.group(2))
    
    if month in early_months:
      year = year - 1
    
    index = year - 2009
    home_coach = coach_dict[home_team_name][index]
    away_coach = coach_dict[away_team_name][index]   
    home_data = [id, home_coach, home_team_name, 1, year]
    away_data = [id, away_coach, away_team_name, 0, year]
    writer.writerow(home_data)
    writer.writerow(away_data)
    count += 1

  wfile.close()
  
if __name__ == '__main__':
  main()