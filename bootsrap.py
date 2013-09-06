import requests


def main():
  url = 'http://getbootstrap.com/examples/navbar-fixed-top/'
  r = requests.get(url)
  print r.content
  
if __name__ == '__main__':
  main()