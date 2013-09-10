import urllib2
import StringIO
from PIL import Image
import pandas as pd
import numpy as np

def main():
  #read in game_ids
  games_data = pd.read_csv('players_copy.csv')
  plyr_ids = np.array(games_data['ID'])
  names = np.array(games_data['Display Name'])

  
  for i in xrange(plyr_ids.shape[0]):
    id = plyr_ids[i]
    name = names[i]
    print name, id
    filename = str(id) + '-' + str(name) + '.png'
    url = 'http://a.espncdn.com/combiner/i?img=/i/headshots/nfl/players/full/%s.png&w=350&h=254' % (id)
    img_exists = True
    try:
      img = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
      img_exists = False
      print e.code
    if img_exists:
      im = Image.open(StringIO.StringIO(img.read()))
      with open(filename, 'wb') as f:
        f.write(img.read()) 
  
  
  
if __name__ == '__main__':
  main()