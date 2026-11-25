
from qanda.models import Pregunta, Respuesta

def eliminar_pregunta(session, pregunta: Pregunta, usuario) -> None:
    """
    Elimina una pregunta verificando antes que el usuario
    tenga permisos de administrador.

    Esta comprobación es una segunda línea de defensa
    además del decorador admin_required.
    """

    if getattr(usuario, "rol", None) != "ADMIN":
        raise PermissionError(
            "Solo un administrador puede eliminar preguntas."
        )

    session.delete(pregunta)


def eliminar_respuesta(session, respuesta: Respuesta, usuario) -> None:
    """
    Elimina una respuesta verificando antes que el usuario
    tenga permisos de administrador.
    """

    if getattr(usuario, "rol", None) != "ADMIN":
        raise PermissionError(
            "Solo un administrador puede eliminar respuestas."
        )

    session.delete(respuesta)
