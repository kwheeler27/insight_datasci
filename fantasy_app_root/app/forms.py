from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, validators, RadioField
from wtforms.validators import Required
   
class RosterForm(Form):
    p1 = TextField('Player 1', validators = [Required()])
    p2 = TextField('Player 2', validators = [Required()])
    p3 = TextField('Player 3', validators = [Required()])
    p4 = TextField('Player 4', validators = [Required()])
    p5 = TextField('Player 5', validators = [Required()])
    p6 = TextField('Player 6', validators = [Required()])
    p7 = TextField('Player 7', validators = [Required()])
    p8 = TextField('Player 8', validators = [Required()])
    p9 = TextField('Player 9', validators = [Required()])
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
