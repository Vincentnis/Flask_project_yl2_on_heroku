from flask_wtf import FlaskForm
from wtforms import (PasswordField, BooleanField, SubmitField, IntegerField, StringField, FileField,
                     widgets, SelectMultipleField, TextAreaField, FormField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, EqualTo, Optional
from wtforms.form import BaseForm


class RegisterForm(FlaskForm):
    surname = StringField('Surname', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    speciality = StringField('Speciality', validators=[DataRequired()])
    about = TextAreaField('Describe yourself(optional)', validators=[Optional()])
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password_again = PasswordField('Password again', validators=[DataRequired(),
                                                                 EqualTo('password', message="Password don't match")])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me?')
    submit = SubmitField('Sign in')


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=True)
    option_widget = widgets.CheckboxInput()


class JobForm(FlaskForm):
    header = StringField('Header', validators=[DataRequired()])
    requirements = TextAreaField('Requirements', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    select = MultiCheckboxField("Label", coerce=int)
    add_category = BooleanField('New category')
    name_of_category = StringField('')
    submit = SubmitField('Submit')


class MyProfile(RegisterForm):
    image = FileField('Choose avatar')
    check_old_password = PasswordField('Enter old password to accept changes', validators=[DataRequired()])
    password = PasswordField('Password')
    password_again = PasswordField('Password again', validators=[EqualTo('password')])
    submit = SubmitField('Edit')


class ChatForm(FlaskForm):
    text = StringField('Message:')
    submit = SubmitField('Send')
