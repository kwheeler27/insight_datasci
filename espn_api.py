import requests
import json
from bs4 import BeautifulSoup
import re

def is_game_row(c):
  return c == 'oddrow' or c == 'evenrow'

def main():
  api_key = '7wyyp5rvmfc5wynqy4akxe42'
  req_format = 'http://api.espn.com/v1/sports/football/nfl/athletes?apikey='
  params = '&limit=3'
  url = req_format + api_key + params

  r = requests.get(url)
  dict = json.loads(r.text)
  players = {}
  athlete_list = dict[u'sports'][0][u'leagues'][0][u'athletes']
  for athlete in athlete_list:
    first_name = athlete[u'firstName'].encode('ascii', 'ignore')
    last_name = athlete[u'lastName'].encode('ascii', 'ignore')
    full_name = athlete[u'fullName'].encode('ascii', 'ignore')
    plyr_id = athlete[u'id']
    href = athlete[u'links'][u'web'][u'athletes'][u'href'].encode('ascii', 'ignore')
    players[plyr_id] = [full_name, first_name, last_name, href]
  print "result count: ", dict[u'resultsCount']
  
  
  #extracts the player name for gamelog requests
  for k, v in players.items():
    href_str = v[3]
    display_name = re.search(r'/([\w-]+-[\w]+)\?', href_str)
    v.append(display_name.group(1))
      
  #gets game_ids for each player
   
  
  id = players.keys()[0]
  name = players[id][4]
  year = 2012
  
  gamelog_url = "http://espn.go.com/nfl/player/gamelog/_/id/%d/year/%d/%s" % (id, year, name)
  gamelog_res = requests.get(gamelog_url)

  soup = BeautifulSoup(gamelog_res.content)
  count = 0
  for tr in soup.find_all('tr', class_=is_game_row):
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    for child in tr.find_all(href=re.compile('/nfl/boxscore')):
      print child
      count += 1
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  print count
  
  
if __name__ == '__main__':
  main()