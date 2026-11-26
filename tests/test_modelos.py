import uuid

import pytest
from werkzeug.security import check_password_hash, generate_password_hash

from qanda.models import Categoria, Etiqueta, Pregunta, Respuesta, Usuario


def test_registrarse_normaliza_email_y_hashea_password():
    usuario = Usuario()

    usuario.registrarse("  Ada Lovelace  ", "  ADA@Example.COM  ", "contraseña123")

    assert usuario.nombre == "Ada Lovelace"
    assert usuario.email == "ada@example.com"
    assert usuario.rol == "GENERAL"
    assert usuario.password_hash != "contraseña123"
    assert check_password_hash(usuario.password_hash, "contraseña123")


@pytest.mark.parametrize(
    ("nombre", "email", "password", "mensaje"),
    [
        ("", "ada@example.com", "contraseña123", "Todos los campos"),
        ("Ada", "", "contraseña123", "Todos los campos"),
        ("Ada", "ada@example.com", "", "Todos los campos"),
        ("Ada", "ada@example.com", "corta", "al menos 8 caracteres"),
        ("Ada", "email-invalido", "contraseña123", "formato válido"),
    ],
)
def test_registrarse_valida_datos(nombre, email, password, mensaje):
    with pytest.raises(ValueError, match=mensaje):
        Usuario().registrarse(nombre, email, password)


def test_autenticarse():
    usuario = Usuario()
    usuario.password_hash = generate_password_hash("contraseña123")

    assert usuario.autenticarse("contraseña123") is True

    with pytest.raises(ValueError, match="obligatoria"):
        usuario.autenticarse("")

    with pytest.raises(ValueError, match="incorrecta"):
        usuario.autenticarse("contraseña456")


def test_realizar_pregunta():
    usuario = Usuario(
        nombre="Ada",
        email="ada@example.com",
        password_hash="hash",
        rol="GENERAL",
    )
    categoria = Categoria(nombre="Python", descrip="Preguntas de Python")

    pregunta = usuario.realizarPregunta(
        "¿Qué es Flask?",
        "Quiero aprender Flask",
        categoria,
    )

    assert isinstance(pregunta, Pregunta)
    assert pregunta.autor is usuario
    assert pregunta.categoria is categoria

    with pytest.raises(ValueError, match="obligatorios"):
        usuario.realizarPregunta("", "Cuerpo", categoria)

    with pytest.raises(ValueError, match="categoría"):
        usuario.realizarPregunta("Título", "Cuerpo", None)


def test_pregunta_crear_valida_y_limpia_datos():
    autor = Usuario(
        nombre="Ada",
        email="ada@example.com",
        password_hash="hash",
        rol="GENERAL",
    )
    categoria = Categoria(nombre="Python", descrip="Preguntas de Python")

    pregunta = Pregunta.crear(
        "  ¿Qué es Flask?  ",
        "  Quiero aprender Flask  ",
        autor,
        categoria,
    )

    assert pregunta.titulo == "¿Qué es Flask?"
    assert pregunta.cuerpo == "Quiero aprender Flask"

    with pytest.raises(ValueError, match="título es obligatorio"):
        Pregunta.crear("   ", "Cuerpo", autor, categoria)

    with pytest.raises(ValueError, match="cuerpo es obligatorio"):
        Pregunta.crear("Título", "   ", autor, categoria)

    with pytest.raises(ValueError, match="debe tener un autor"):
        Pregunta.crear("Título", "Cuerpo", None, categoria)

    with pytest.raises(ValueError, match="debe tener una categoría"):
        Pregunta.crear("Título", "Cuerpo", autor, None)


def test_agregar_y_quitar_etiqueta():
    pregunta = Pregunta(titulo="Título", cuerpo="Cuerpo")
    etiqueta = Etiqueta(nombre="Python")

    pregunta.agregarEtiqueta(etiqueta)
    pregunta.agregarEtiqueta(etiqueta)

    assert pregunta.etiquetas == [etiqueta]

    with pytest.raises(ValueError, match="no puede ser nula"):
        pregunta.agregarEtiqueta(None)

    pregunta.quitarEtiqueta(etiqueta)

    assert pregunta.etiquetas == []

    pregunta.quitarEtiqueta(Etiqueta(nombre="Inexistente"))


def test_aceptar_respuesta_y_tiene_respuesta_aceptada():
    autor = Usuario(
        nombre="Ada",
        email="ada@example.com",
        password_hash="hash",
        rol="GENERAL",
    )
    autor.id = uuid.uuid4()

    otro = Usuario(
        nombre="Otro",
        email="otro@example.com",
        password_hash="hash",
        rol="GENERAL",
    )
    otro.id = uuid.uuid4()

    pregunta = Pregunta(titulo="Título", cuerpo="Cuerpo")
    pregunta.id = uuid.uuid4()
    pregunta.autor_id = autor.id

    respuesta = Respuesta(cuerpo="Primera")
    respuesta.id = uuid.uuid4()
    respuesta.pregunta_id = pregunta.id
    respuesta.aceptacion = False

    otra_pregunta = uuid.uuid4()
    respuesta_ajena = Respuesta(cuerpo="Ajena")
    respuesta_ajena.id = uuid.uuid4()
    respuesta_ajena.pregunta_id = otra_pregunta
    respuesta_ajena.aceptacion = False

    segunda = Respuesta(cuerpo="Segunda")
    segunda.id = uuid.uuid4()
    segunda.pregunta_id = pregunta.id
    segunda.aceptacion = False

    pregunta.respuestas = [respuesta, segunda]

    assert pregunta.tieneRespuestaAceptada() is False

    with pytest.raises(ValueError, match="Solo el autor"):
        pregunta.aceptarRespuesta(respuesta, otro)

    with pytest.raises(ValueError, match="no pertenece"):
        pregunta.aceptarRespuesta(respuesta_ajena, autor)

    pregunta.aceptarRespuesta(respuesta, autor)

    assert respuesta.aceptacion is True
    assert pregunta.tieneRespuestaAceptada() is True

    pregunta.aceptarRespuesta(segunda, autor)

    assert respuesta.aceptacion is False
    assert segunda.aceptacion is True
    assert pregunta.tieneRespuestaAceptada() is True
