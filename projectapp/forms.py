from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired,Email,Length
from flask_wtf.file import FileField, FileAllowed

class InvitationForm(FlaskForm):
    ivcard = FileField('Upload I.V: ', validators=[FileAllowed(upload_set=['pdf'],message='Upload a valid IV')])
    message = StringField('Your message')
    submit = SubmitField('Upload')
