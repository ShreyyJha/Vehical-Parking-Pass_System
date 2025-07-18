from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

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
    vehicle_type = SelectField('Vehicle Type', choices=[('Car', 'Car'), ('Bike', 'Bike')], validators=[DataRequired()])
    submit = SubmitField('Apply')
