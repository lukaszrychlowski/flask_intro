from flask import Flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, DateField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app import email
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('user', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired(), Email()])
    password = StringField('password', validators=[DataRequired()])
    password2 = StringField('repeat pw', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('username already taken')
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('email address already taken')

class EditProfileForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    submit = SubmitField('submit')


class EmptyForm(FlaskForm):
    submit = SubmitField('submit')

class PostForm(FlaskForm):
    post = TextAreaField('say smth', validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('submit')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('email', validators=[DataRequired(), Email()])
    submit = SubmitField('password reset')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('password', validators=[DataRequired()])
    password2 = PasswordField('repeat pw', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('req a new pw')

class CastingsForm(FlaskForm):
    casting_no = IntegerField('casting no.', validators=[DataRequired()])
    casting_date = DateField('casting date')
    casting_composition = StringField('chemical composition', validators=[DataRequired()])
    submit = SubmitField('add')

class ExtrusionForm(FlaskForm):
    extrusion_no = IntegerField('extr. no.', validators=[DataRequired()])
    extrusion_composition = StringField('chemical composition', validators=[DataRequired()])
    submit = SubmitField('add')