import sys
import MySQLdb as mdb


#create DB
def connect():
  db = mdb.connect(host='localhost', user='root', db='crashcourse') #local_infile = 1 used if loading from local csv)
  db.autocommit(True)
  return db, db.cursor()


def main():
  db = connect()[0]
  cur = connect()[1]
  command = "select * from customers"
  output = cur.execute(command)
  rows = cur.fetchall()
  print rows
   
  cur.close()
  del cur

  db.close()
  del db
  
if __name__ == '__main__':
  main()