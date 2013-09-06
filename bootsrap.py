import requests


def main():
  url = 'http://getbootstrap.com/examples/sticky-footer/'
  r = requests.get(url)
  print r.content
  
if __name__ == '__main__':
  main()