"""
Validaciones
"""

from collections.abc import Container
from datetime import date

from typer import Exit


def validar_fecha(fecha: str) -> date:
    """Validar que la fecha tenga el formato AAAA-MM-DD"""
    try:
        return date.fromisoformat(fecha)
    except ValueError:
        raise Exit(1)


def validar_nivel(nivel: int) -> None:
    """Validar que el nivel sea un entero comprendido entre 1 y 4"""
    if not isinstance(nivel, int) or isinstance(nivel, bool) or not (1 <= nivel <= 4):
        raise Exit(1)


def validar_tipo_juicio(tipo_juicio: str, tipos_juicios: Container[str]) -> None:
    """Validar que el tipo de juicio sea uno de los permitidos"""
    if tipo_juicio not in tipos_juicios:
        raise Exit(1)
