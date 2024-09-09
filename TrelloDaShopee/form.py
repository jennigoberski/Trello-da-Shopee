from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.choices import SelectField
from wtforms.fields.datetime import DateTimeField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, Length, EqualTo, Optional


class LoginForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')


class CreateBoardForm(FlaskForm):
    name = StringField('Nome do Quadro', validators=[DataRequired(), Length(min=3, max=150)])
    submit = SubmitField('Criar Quadro')


class EditCardForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    start_time = DateTimeField('Start Time', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    end_time = DateTimeField('End Time', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    status = StringField('Status', validators=[Optional()])
    column_id = SelectField('Column', coerce=int, validators=[DataRequired()])
