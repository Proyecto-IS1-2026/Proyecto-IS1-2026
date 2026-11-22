from qanda.models import Pregunta


def eliminar_pregunta(session, pregunta: Pregunta, usuario) -> None:
    """
    Elimina una pregunta verificando antes que el usuario tenga permisos.

    Es una segunda línea de defensa además del decorador `admin_required`:
    recibe el usuario explícitamente para poder validarse fuera del contexto
    de la request.
    """

    if getattr(usuario, "rol", None) != "ADMIN":
        raise PermissionError("Solo un administrador puede eliminar preguntas.")

    session.delete(pregunta)
