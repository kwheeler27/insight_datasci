import sys
from bs4 import BeautifulSoup
import requests
import re

def is_game_row(c):
  return c == 'oddrow' or c == 'evenrow'

def main():  
  game_id = 0
  url = "http://espn.go.com/nfl/player/gamelog/_/id/10452/year/2009/adrian-peterson"
  r = requests.get(url)

  soup = BeautifulSoup(r.content)
  count = 0
  for tr in soup.find_all('tr', class_=is_game_row):
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    for child in tr.find_all(href=re.compile('/nfl/boxscore')):
      print child
      count += 1
    print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
  

  print game_id
  print count


if __name__ == '__main__':
  main()