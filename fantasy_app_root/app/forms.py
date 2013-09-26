from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, validators, RadioField
from wtforms.validators import Required
   
class RosterForm(Form):
    p1 = TextField('Tom Brady', validators = [Required()])
    p2 = TextField('Adrian Peterson', validators = [Required()])
    p3 = TextField('Doug Martin', validators = [Required()])
    p4 = TextField('Jimmy Graham', validators = [Required()])
    p5 = TextField('A.J. Green', validators = [Required()])
    p6 = TextField('Aaron Rodgers', validators = [Required()])
    p7 = TextField('Brandon Marshall', validators = [Required()])
    p8 = TextField('Matt Prater', validators = [Required()])
    p9 = TextField('Vernon Davis', validators = [Required()])
    p10 = TextField('Player 10', validators = [Required()])
    p11 = TextField('Player 11', validators = [Required()])
    p12 = TextField('Player 12', validators = [Required()])
    p13 = TextField('Player 13', validators = [Required()])
    p14 = TextField('Player 14', validators = [Required()])
    p15 = TextField('Player 15', validators = [Required()])
    p16 = TextField('Player 16', validators = [Required()])
    p17 = TextField('Player 17', validators = [Required()])
    p18 = TextField('Player 18', validators = [Required()])
    p19 = TextField('Player 19', validators = [Required()])
    p20 = TextField('Player 20', validators = [Required()])
