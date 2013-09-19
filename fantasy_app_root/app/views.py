from app import app
from flask import render_template, flash, redirect, url_for, request, jsonify, session
from forms import RosterForm
import MySQLdb as mdb
import json
from mn_predictions import *

@app.route('/players', methods = ['GET'])
def players():
  con = mdb.connect(host='localhost', db='fantasy_lineups', user='root', passwd='r')
  cur = con.cursor()
  #test
  command = "SELECT DISTINCT(name), position FROM players;"
  output = cur.execute(command)
  rows = cur.fetchall()

  temparr = []
  for row in rows:
    display_name = row[0]
    pos = row[1]
    n = display_name.replace('-',' ')
    if pos in ['WR', 'RB', 'QB', 'TE', 'PK', 'FB']:
      temparr.append({'value':'%s' % n.title(),
                   'tokens':n.split(' '),
                   'datum':{'value':'%s' % n.title(),'position':row[1]}, 'tokens':n.split(' ')})
                   
  cur.close()
  con.close()
  return json.dumps(temparr)



@app.route('/', methods = ['GET', 'POST'])
@app.route('/home', methods = ['GET', 'POST'])
def index():
    form = RosterForm()
    m = False
    if form.validate_on_submit():
      flash('Roster Flash: ' + form.p1.data)
      return redirect('/optimize')
    return render_template("home.html", title = 'Home', form = form, m=m)

@app.route('/algorithm')
def algorithm():
    return render_template("algorithm.html")
        
@app.route('/slides')
def slides():
    return render_template("slides.html")
    
@app.route('/validation')
def validation():
    return render_template("validation.html")
    
@app.route('/optimize', methods = ['POST'])
def optimize():
  session['form'] = request.form
    
  return redirect(url_for('results'))
    
@app.route('/results')
def results():
  form = session['form']
  
  if 'week' not in form:
    form = RosterForm()
    m = True
    return render_template("home.html", title = 'Home', form = form, m=m)
    
  week = get_week(form) 
  plyrs = plyr_names(form) #check if each name is valid
  predictions = make_predictions(plyrs, week)
  
  qb = []
  wr = []
  rb = []
  te = []
  pk = []
  d = []  
  if 'QB' in predictions:
    qb.append(predictions['QB'])
  if 'RB' in predictions:
    rb.append(predictions['RB'])
  if 'WR' in predictions:
    wr.append(predictions['WR'])
  if 'TE' in predictions:
    te.append(predictions['TE'])
  if 'K' in predictions:
    pk.append(predictions['K'])
  
  return render_template("results.html", form=form, qb=qb, wr=wr, rb=rb, te=te, pk=pk, d=d)
  
  
  
  
  
  
