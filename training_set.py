import time
import csv
import numpy as np
import pandas as pd
import string

def plyr_game_ids(id, games_data):
  game_ids = []
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
  
  #gets player training set
  plyr_id = 43
  plyr_X = create_training_set(plyr_id, games_data, plyr_ids)
  
  
  
  end_time = time.time()
  print("Elapsed time was %g seconds" % (end_time - start_time))  
  #fantasy_frame = pd.DataFrame(consolidated_scores, columns=['game_id','plyr_id', 'name', 'fntsy_pts'])
  plyr_X.to_csv('test.csv')

  
if __name__ == '__main__':
  main()
  
