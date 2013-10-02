import MySQLdb as mdb


#connect to MySQL
def connect():
  db = mdb.connect(host='localhost', db='fantasy_lineups', user='root', passwd='r')
  db.autocommit(True)
  return db, db.cursor()
  
def is_game_row(c):
  return c == 'oddrow' or c == 'evenrow'
  
def get_coach_dict():
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
  return coach_dict