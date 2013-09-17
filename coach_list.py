import requests
import re
import time
import csv
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def is_team_row(c):
  return c == 'oddrow' or c == 'evenrow'

def main():
  
  wfile = open("coach_data.csv", "wb")
  field_names = ['game_id','coach_id', 'team', 'is_home', 'year']
  writer = csv.writer(wfile)
  writer.writerow(field_names)
  
  coach_dict = {}
  coach_dict['buf'] = [80,81,81,81,105]
  coach_dict['mia'] = [65,65,65,97,97]
  coach_dict['ne'] = [2,2,2,2,2]
  coach_dict['nyj'] = [72,72,72,72,72]
  coach_dict['den'] = [73,73,13,13,13]
  coach_dict['kc'] = [77,77,77,49,23]
  coach_dict['oak'] = [69,69,69,98,98]
  coach_dict['sd'] = [44,44,44,44,44]
  coach_dict['bal'] = [68,68,68,68,68]
  coach_dict['cin'] = [18,18,18,18,18]
  coach_dict['cle'] = [54,54,92,92,101]
  coach_dict['pit'] = [63,63,63,63,63]
  coach_dict['hou'] = [56,56,56,56,56]
  coach_dict['ind'] = [76,76,76,99,99]
  coach_dict['jac'] = [5,5,5,43,108]
  coach_dict['ten'] = [12,12,94,94,94]
  coach_dict['dal'] = [85,85,85,85,85]
  coach_dict['nyg'] = [35,35,35,35,35]
  coach_dict['phi'] = [23,23,23,23,103]
  coach_dict['wsh'] = [25,25,25,25,25]
  coach_dict['ari'] = [59,59,59,59,107]
  coach_dict['stl'] = [50,50,50,12,12]
  coach_dict['sf'] = [70,70,91,91,91]
  coach_dict['sea'] = [83,83,83,83,83]
  coach_dict['chi'] = [38,38,38,38,102]
  coach_dict['det'] = [71,71,71,71,71]
  coach_dict['gb'] = [58,58,58,58,58]
  coach_dict['atl'] = [67,67,67,67,67]
  coach_dict['min'] = [86,86,86,86,86]
  coach_dict['car'] = [13,13,90,90,90]
  coach_dict['no'] = [42,42,42,50,42]
  coach_dict['tb'] = [75,75,75,100,100]
  
  games_data = pd.read_csv('games-data.csv')
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
    
    print count, id, home_coach, home_team_name, year
    print count, id, away_coach, away_team_name
    writer.writerow(home_data)
    writer.writerow(away_data)
    count += 1
    
  '''
  coaches_url = "http://espn.go.com/nfl/coaches"
  coach_res = requests.get(coaches_url)
  soup = BeautifulSoup(coach_res.content)
  table = soup.find('table', class_="tablehead")
  count = 1
  for row in table.find_all('tr', class_=is_team_row):
    cols = row.find_all('td')
    href = cols[0].find_all('a')
    href_str = str(href)
    coach_id = re.search(r'/id/(\d+)/([\w.\'-]+-[\w\']+)', href_str)    
    t_href = cols[3].find_all('a')
    t_href_str = str(t_href)
    team_id = re.search(r'/name/(\w+)/', t_href_str)
    team = team_id.group(1)
       
    if coach_id:
      data = [int(coach_id.group(1)), coach_id.group(2), team, 2013]
      print data, count
      count += 1
      #writer.writerow(data)
  '''
  wfile.close()
  
if __name__ == '__main__':
  main()