from app import app
from flask import render_template


@app.route('/')
@app.route('/home')
def index():
    user = { 'nickname': 'Kevin' } # fake user
    return render_template("home.html", title = 'Home', user = user)

@app.route('/algorithm')
def slides():
    return render_template("algorithm.html")
        
@app.route('/slides')
def slides():
    return render_template("slides.html")
    
@app.route('/optimize', methods = ['POST'])
def optimize():
    session['user'] = request.form['user']
    return redirect(url_for('results'))
    
@app.route('/results')
def results():
  return render_template("results.html")
