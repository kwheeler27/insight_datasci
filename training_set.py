import time
import math
import csv
import numpy as np
import pandas as pd
from sklearn.naive_bayes import BernoulliNB, MultinomialNB

def plyr_game_ids(id, games_data):
  game_indices = np.where(games_data['plyr_id'] == id)
  return games_data['game_id'][game_indices[0]]  

def update_training_matrix(plyrs_in_game, game, X):
  for p in plyrs_in_game:
    X.ix[game][p] = 1
  return

def populate_training_set(X, games_arr, game_plyr_df):
  for game in games_arr:
    indices = np.where(game_plyr_df['game_id'] == game)
    plyrs_in_game = game_plyr_df['plyr_id'][indices[0]]
    update_training_matrix(plyrs_in_game, game, X)
  return
  
def create_training_set(plyr_id, games_data, all_plyrs):
  games =  plyr_game_ids(plyr_id, games_data)
  n_cols = all_plyrs.shape[0]
  m_rows = games.shape[0]
  zeros = np.zeros((m_rows, n_cols))
  X = pd.DataFrame(zeros, index=games, columns=all_plyrs)
  populate_training_set(X, games, games_data)
  return X

def plyr_fantasy_pts(plyr_id, plyr_game_ids, fantasy_scores):
  indices = np.where(fantasy_scores['plyr_id'] == plyr_id)
  y = fantasy_scores['fntsy_pts'][indices[0]]
  return y

def discretize(arr):
  result = []
  
  for i in arr:
    if i <= 2.5:
      result.append(0)
    elif i > 2.5 and i <= 5.0:
      result.append(1)
    elif i > 5.0 and i <= 7.5:
      result.append(2)
    elif i > 7.5 and i <= 10.0:
      result.append(3)       
    elif i > 10.0 and i <= 12.5:
      result.append(4)
    elif i > 12.5 and i <= 15.0:
      result.append(5)
    elif i > 15 and i <= 17.5:
      result.append(6)
    elif i > 17.5 and i <= 20.0:
      result.append(7)       
    elif i > 20.0 and i <= 22.5:
      result.append(8)
    elif i > 22.5 and i <= 25.0:
      result.append(9)
    elif i > 25.0 and i <= 27.5:
      result.append(10)
    elif i > 27.5 and i <= 30:
      result.append(11)
    else:
      result.append(12)
  return np.array(result)       

def get_ninety_percent(l):
  return int(math.floor(l * 0.99))  


def main():
  start_time = time.time()
  #read in game IDs
  games_data = pd.read_csv('games-data.csv')
  all_games = np.array(games_data['game_id'])
  all_plyrs = np.array(games_data['plyr_id'])
  uni_game_ids = np.unique(all_games)
  
  #read in player IDs
  player_data = pd.read_csv('players.csv')
  plyr_ids = np.unique(np.array(player_data['ID']))
  
  #read in fantasy scores
  fantasy_scores = pd.read_csv('fantasy_scores.csv')
  
  #gets player training matrix
  plyr_id = 8439
  X = create_training_set(plyr_id, games_data, plyr_ids)
  index = get_ninety_percent(len(np.array(X.index))) #for cross-validation
  train_X = X[:index]
  test_X = X[index:]
  
  #gets training output vector
  plyr_game_ids = np.array(train_X.index)
  scores = plyr_fantasy_pts(plyr_id, plyr_game_ids, fantasy_scores)
  Y = discretize(scores.values)
  train_Y = Y[:index]
  test_Y = Y[index:]
  
  #run Bernoulli NB Classifier
  nb_clf = BernoulliNB()
  nb_clf.fit(train_X, train_Y)
  nb_predictions = nb_clf.predict(test_X)
  
  #run Multinomial NB Classifier
  mn_clf = MultinomialNB()
  mn_clf.fit(train_X, train_Y)
  mn_predictions = nb_clf.predict(test_X)
  
  #test for game, fantasy score alignment  
  for i in xrange(test_Y.shape[0]):
    print plyr_game_ids[i], scores.values[i], test_Y[i], nb_predictions[i], mn_predictions[i]
  
  print "Bernoulli NB accuracy: ", nb_clf.score(test_X, test_Y)
  print "Multinomial NB accuracy: ", mn_clf.score(test_X, test_Y)
  end_time = time.time()
  print("Elapsed time was %g seconds" % (end_time - start_time))  
  #plyr_X.to_csv('test.csv')

  
if __name__ == '__main__':
  main()
  
