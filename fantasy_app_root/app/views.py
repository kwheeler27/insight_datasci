from app import app
from flask import render_template, flash, redirect
from forms import RosterForm

@app.route('/', methods = ['GET', 'POST'])
@app.route('/home', methods = ['GET', 'POST'])
def index():
    form = RosterForm()
    user = { 'nickname': 'Kevin' } # fake user
    if form.validate_on_submit():
      flash('Login requested for OpenID="' + form.openid.data + '", remember_me=' + str(form.remember_me.data))
      return redirect('/optimize')
    return render_template("home.html", title = 'Home', user = user, form = form)

@app.route('/algorithm')
def algorithm():
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
