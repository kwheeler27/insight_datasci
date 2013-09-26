import requests


def main():
  url = 'http://scores.espn.go.com/nfl/boxscore?gameId=330908014'
  r = requests.get(url)
  print r.content
  
if __name__ == '__main__':
  main()