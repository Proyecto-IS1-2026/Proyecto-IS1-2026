
from flask import (
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import login_required, login_user, logout_user
from sqlalchemy import select

from qanda.auth import auth_bp
from qanda.models import Usuario


# Ruta encargada de registrar nuevos usuarios en el sistema.
@auth_bp.route("/register", methods=["GET", "POST"])
def register():

    # Si la solicitud es GET muestra el formulario de registro.
    if request.method == "GET":
        return render_template("auth/register.html")

    # Obtiene los datos ingresados por el usuario en el formulario.
    nombre = request.form.get("nombre", "")
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirmar_password = request.form.get("confirmar_password", "")

    # Comprueba que las dos contraseñas ingresadas coincidan.
    if password != confirmar_password:
        flash("Las contraseñas no coinciden.", "error")
        return redirect(url_for("auth.register"))

    session_factory = current_app.extensions["db_session_factory"]

    try:
        with session_factory.begin() as session:
            usuario_existente = session.scalar(
                select(Usuario).where(Usuario.email == email)
            )

            if usuario_existente:
                raise ValueError("Ya existe un usuario con ese email.")

            usuario = Usuario()
            usuario.registrarse(nombre, email, password)

            session.add(usuario)

    except ValueError as error:
        flash(str(error), "error")
        return redirect(url_for("auth.register"))

    flash("Tu cuenta fue creada correctamente.", "success")
    return redirect(url_for("auth.login"))


# Ruta encargada de permitir que los usuarios inicien sesión.
@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # Si la solicitud es GET muestra el formulario de inicio de sesion.
    if request.method == "GET":
        return render_template("auth/login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        flash("Debés ingresar email y contraseña.", "error")
        return redirect(url_for("auth.login"))

    session_factory = current_app.extensions["db_session_factory"]

    with session_factory() as session:
        usuario = session.scalar(
            select(Usuario).where(Usuario.email == email)
        )

        if usuario is not None:
            try:
                usuario.autenticarse(password)
            except ValueError:
                usuario = None

    if usuario is None:
        flash("Email o contraseña incorrectos.", "error")
        return redirect(url_for("auth.login"))

    login_user(usuario)

    flash("Iniciaste sesión correctamente.", "success")
    return redirect(url_for("web.index"))


# Ruta encargada de cerrar la sesión del usuario actual.
@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Cerraste sesión correctamente.", "success")
    return redirect(url_for("web.index"))
