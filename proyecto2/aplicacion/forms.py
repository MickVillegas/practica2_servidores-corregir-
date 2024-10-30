from flask_wtf import FlaskForm
from wtforms import DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField

class formArticulo(FlaskForm):
    nombre = StringField('Nombre:', validators=[DataRequired("Tienes que introducir el dato")])
    precio = DecimalField('Precio:', default=0, validators=[DataRequired("Tienes que introducir el dato")])
    iva = IntegerField('IVA', validators=[DataRequired("Tienes que introducir el dato")])
    descripcion = TextAreaField('Descripcion:')
    photo = FileField('Selecciona imagen:')
    stock = IntegerField('Stock:', default=1, validators=[DataRequired("Tienes que introducir el dato")])
    CategoriaId = SelectField('Categoria:', coerce=int)
    submit = SubmitField('Enviar')
class formCategoria(FlaskForm):
    nombre = StringField("Nombre: ", validators=[DataRequired("tienes que introducir datos")])
    submit = SubmitField('Enviar')
class formSINO(FlaskForm):
    si = SubmitField("Si")
    no = SubmitField("No")
class LoginForm(FlaskForm):
    username = StringField("Login", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Entrar")
class formUsuario(FlaskForm):
    username = StringField("Login", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Entrar")
class formChangePassword(FlaskForm):
    password = PasswordField('Password', validators = [DataRequired()])
    submit = SubmitField('Aceptar')

from wtforms import HiddenField
from wtforms.validators import NumberRange
class formCarrito(FlaskForm):
    id = HiddenField()
    cantidad = IntegerField('Cantidad', default=1,
                            validators=[NumberRange(min = 1,
                                                    message="Debe ser un numero positivo"),
                                                    DataRequired("Tienes que introducir el dato")])
    submit = SubmitField('Aceptar')
