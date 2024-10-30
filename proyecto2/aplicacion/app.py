import os
from flask import Flask, abort, redirect, render_template, request, url_for, session
from flask_bootstrap import Bootstrap5
from aplicacion import config
from aplicacion.forms import formArticulo, formCategoria, formSINO, formUsuario, formChangePassword, LoginForm, formCarrito
from werkzeug.utils import secure_filename
from aplicacion.models import Categorias, Articulos, Usuarios
from flask import make_response
import json

app = Flask(__name__)
from aplicacion.login import login_user, logout_user, is_admin, is_login

Bootstrap = Bootstrap5(app)
app.config.from_object(config)

#@app.context_processor
#def login():
#    if "id" in session:
#        return {'is_login': True}
#    else:
#        return {'is_login': False}
    
#@app.context_processor
#def admin():
#    return {'is_admin': session.get("admin", False)}

from aplicacion.models import Articulos, Categorias, Usuarios, db
from flask_login import login_user, logout_user, login_required, current_user, LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
@login_manager.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))

db.init_app(app)


@app.route("/")
@app.route("/categorias/<id>")
def inicio (id = '0'):
    categoria = Categorias.query.get(id)
    if id == '0':
        articulos = Articulos.query.all()
    else:
        articulos = Articulos.query.filter_by(CategoriaId = id)
    categorias = Categorias.query.all()
    return render_template("inicio.html", categoria = categoria, articulos = articulos, categorias = categorias)
@app.route('/categorias')
def categorias():
    categorias = Categorias.query.all()
    return render_template('categorias.html', categorias = categorias)
@app.errorhandler(404)
def pageNotFOund(error):
    return render_template("error.html", error = "pagina no encontrada..."), 404

@app.route('/articulos/new/', methods = ['GET', 'POST'])
def articulos_new():
    if not is_admin():
        abort(404)
    form = formArticulo()
    categorias = [(c.id, c.nombre) for c in Categorias.query.all()[0:]]
    form.CategoriaId.choices = categorias
    if form.validate_on_submit():
        try:
            f = form.photo.data
            nombre_fichero = secure_filename(f.filename)
            f.save(app.root_path+"static/upload"+nombre_fichero)
        except:
            nombre_fichero = ""
        art = Articulos()
        form.populate_obj(art)
        art.image = nombre_fichero
        db.session.add(art)
        db.session.commit()
        return redirect(url_for("inicio"))
    else:
        return render_template("articulos_new.html", form = form)

@app.route('/categorias/new', methods = ["get", "post"])
@login_required
def categorias_new():
    #if not is_admin():
    if not current_user.is_admin():
        abort(404)
    form = formCategoria(request.form)
    if form.validate_on_submit():
        cat = Categorias(nombre = form.nombre.data)
        db.session.add(cat)
        db.session.commit()
        return redirect(url_for("categorias"))
    else:
        return render_template("categorias_new.html", form = form)

@app.route('/articulos/<id>/edit', methods = ["get", "post"])
@login_required
def articulos_edit(id):
    #if not is_admin():
    if not current_user.is_admin():
        abort(404)
    art = Articulos.query.get(id)
    if art is None:
        abort(404)
    form = formArticulo(obj = art)
    categorias = [(c.id, c.nombre) for c in Categorias.query.all()[0:]]
    form.CategoriaId.choices = categorias
    if form.validate_on_submit():
        if form.photo.data:
            os.remove(app.root_path + "/img/upload/" + art.image)
            try:
                f = form.photo.data
                nombre_fichero = secure_filename(f.filename)
                f.save(app.root_path + "/img/upload/" + nombre_fichero)
            except:
                nombre_fichero = ""
        else:
            nombre_fichero = art.image
        form.populate_obj(art)
        art.image = nombre_fichero
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("articulos_new.html", form = form)

@app.route('/articulos/<id>/delete', methods = ["get", "post"])
@login_required
def articulos_delete(id):
    #if not is_admin():
    if not current_user.is_admin():
        abort(404)
    art = Articulos.query.get(id)
    if art is None:
        abort(404)
    form = formSINO()
    if form.validate_on_submit():
        if form.si.data:
            if art.image!="":
                os.remove(app.root_path+"/static/img"+art.image)
            db.session.delete(art)
            db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("articulos_delete.html", form = form, art = art)

@app.route('/categorias/<id>/edit', methods = ["get", "post"])
@login_required
def categorias_edit(id):
    #if not is_admin():
    if not current_user.is_admin():
        abort(404)
    cat = Categorias.query.get(id)
    if cat is None:
        abort(404)
    form = formCategoria(request.form, obj = cat)
    if form.validate_on_submit():
        form.populate_obj(cat)
        db.session.commit()
        return redirect(url_for("categorias"))
    return render_template("categorias_new.html", form = form)

@app.route('/categorias/<id>/delete', methods = ["get", "post"])
@login_required
def categorias_delete(id):
    #if not is_admin():
    if not current_user.is_admin():
        abort(404)
    cat = Categorias.query.get(id)
    if cat is None:
        abort(404)
    form = formSINO()
    if form.validate_on_submit():
        if form.si.data:
            db.session.delete(cat)
            db.session.commit()
        return redirect(url_for("categorias"))
    return render_template("categorias_delete.html", form = form, cat = cat)


@app.route('/login', methods = ["get", "post"])
def login():
    #if is_login():
    if not current_user.is_authenticated:
        return redirect(url_for("inicio"))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuarios.query.filter_by(username = form.username.data).first()
        if user!=None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(next or url_for('inicio'))
        form.username.errors.append("Usuarios o contraseña incorrectas.")
    return render_template('loing,html', form = form)
    
@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/registro", methods = ["get", "post"])
def registro():
    #if is_login():
    if current_user.is_authenticated:
        return redirect(url_for("inicio"))
    form = formUsuario()
    if form.validate_on_submit():
        existe_usuario = Usuarios.query.filter_by(username = form.username.data).first()
        if existe_usuario == None:
            user = Usuarios()
            form.populate_obj(user)
            user.admin = False
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("inicio"))
        form.username.errors.append("Nombre de usuario ya existe")
    return render_template("usuarios_new.html", form = form)

@app.route('/perfil/<username>', methods = ["get", "post"])
@login_required
def perfil(username):
    #if not is_login():
     #   return redirect(url_for("inicio"))
    user = Usuarios.query.filter_by(username = username).first()
    if user is None:
        abort(404)
    form = formUsuario(request.form, obj = user)
    del form.password
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("usuarios_new.html")

@app.route('/changepassword/<username>', methods = ["get", "post"])
@login_required
def changepassword(username):
    #if not is_login():
      #  return redirect(url_for("inicio"))
    user = Usuarios.query.filter_by(username = username).first()
    if user is None:
        abort(404)
    form = formChangePassword()
    if form.validate_on_submit():
        form.populate_obj(user)
        db.session.commit()
        return redirect(url_for("inicio"))
    return render_template("changepassword.html", form = form)

@app.route('/carrito/add/<id>', methods = ["get", "post"])
@login_required
def carrito_add(id):
    art = Articulos.query.get(id)
    form = formCarrito()
    form.id.data = id
    if form.validate_on_submit():
        if art.stock>=int(form.cantidad.data):
            try:
                datos = json.loads(request.cookies.get(str(current_user.id)))
            except:
                datos = []
            actualizar = False
            for dato in datos:
                if int(dato["id"]) == id:
                    dato["cantidad"] = form.cantidad.data
                    actualizar = True
            if not actualizar:
                datos.append({"id":form.id.data, "cantidad": form.cantidad.data})
            resp = make_response(redirect(url_for('inicio')))
            resp.set_cookie(str(current_user.id), json.dumps(datos))
            return resp
        form.cantidad.errors.append("No hay articulos suficientes.")
    return render_template("carrito_add.html", form = form, art = art)


@app.route('/carrito')
@login_required
def carrito():
    try:
        datos = json.loads(request.cookies.get(str(current_user.id)))
    except:
        datos = []
    
    articulos = []
    cantidades = []
    total = 0

    for articulo in datos:
        articulos.append(Articulos.query.get(articulo["id"]))
        cantidades.append(articulo["cantidad"])
        total = total + Articulos.query.get(articulo["id"]).precio_final() * articulo["cantidad"]
    articulos = zip(articulos, cantidades)

    return render_template("carrito.html", articulos = articulos, total = total)

@app.context_processor
def contar_carrito():
    if not current_user.is_authenticated:
        return {'num_articulos': 0}
    if request.cookies.get(str(current_user.id)) is None:
        return {'num_articulos': 0}
    else:
        datos = json.loads(request.cookies.get(str(current_user.id)))
        return {'num_articulos': len(datos)}
    
@app.route('/carrito_delete/<id>')
@login_required
def carrito_delete(id):
    try:
        datos = json.loads(request.cookies.get(str(current_user.id)))
    except:
        datos = []
    new_datos = []
    for dato in datos:
        if dato["id"] != id:
            new_datos.append(dato)
    resp = make_response(redirect(url_for('carrito')))
    resp.set_cookie(str(current_user.id, json.dumps(new_datos)))
    return resp

@app.route('/pedido')
@login_required
def pedido():
    try:
        datos = json.loads(request.cookies.get(str(current_user.id)))
    except:
        datos = []
    total = 0
    for articulo in datos:
        total = total + Articulos.query.get(articulo["id"]).precio_final()*articulo["cantidad"]
        Articulos.query.get(articulo["id"]).stock -=articulo["cantidad"]
        db.session.commit()
    resp = make_response(render_template("pedido.html", total = total))
    resp.set_cookie(str(current_user.id), "", expires = 0)
    return resp