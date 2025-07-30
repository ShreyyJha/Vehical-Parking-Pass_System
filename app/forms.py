from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ApplicationForm(FlaskForm):
    vehicle_number = StringField('Vehicle Number', validators=[DataRequired()])
    vehicle_type = SelectField('Vehicle Type', choices=[('Four-Wheeler', 'Four-Wheeler'), ('Two-Wheeler', 'Two-Wheeler')], validators=[DataRequired()])
    mobile_number = StringField('Mobile Number', validators=[DataRequired(), Length(min=10, max=15)])
    photo = FileField('Upload Photo')
    submit = SubmitField('Apply')
