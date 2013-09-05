import requests
import json
import re
import time
import csv

def is_game_row(c):
  return c == 'oddrow' or c == 'evenrow'

def main():
  api_key = '7wyyp5rvmfc5wynqy4akxe42'
  req_format = 'http://api.espn.com/v1/sports/football/nfl/athletes?apikey='
  offset = '&offset=5&limit=10'
  count = 0
  num_players = 3254
  players = {}
  wfile = open("test.csv", "wb")
  c = csv.writer(wfile)
  c.writerow(["ID", "Full Name","First Name","Last Name","Player URL","Display Name"])
  #while count < num_players:
  url = req_format + api_key + offset
  r = requests.get(url)
  dict = json.loads(r.text)
  #result_count = dict[u'resultsCount'] 
  print "count: ", count
  athlete_list = dict[u'sports'][0][u'leagues'][0][u'athletes']
  for athlete in athlete_list:
    print "keys: ", athlete.keys()
    first_name = athlete[u'firstName'].encode('ascii', 'ignore')
    last_name = athlete[u'lastName'].encode('ascii', 'ignore')
    full_name = athlete[u'fullName'].encode('ascii', 'ignore')
    plyr_id = athlete[u'id']
    href = athlete[u'links'][u'web'][u'athletes'][u'href'].encode('ascii', 'ignore')
    players[plyr_id] = [plyr_id, full_name, first_name, last_name, href]
    
  
  #extracts the player name for gamelog requests
  for k, v in players.items():
    href_str = v[4]
    display_name = re.search(r'/([\w-]+-[\w]+)\?', href_str)
    v.append(display_name.group(1))
    c.writerow(v)  
    print k, v[5]
  #gets game_ids for each player
  print len(players.keys())
  wfile.close()
   
  '''
  id = 10682
  name = players[id][4]
  year = 2009
  
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
  '''
  
if __name__ == '__main__':
  main()