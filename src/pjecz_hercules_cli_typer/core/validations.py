"""
Validations

Funciones para validar y normalizar los parámetros de consulta.
Si un texto queda vacío después de normalizar, entregan una cadena vacía para que el filtro se ignore.
"""

import re
import uuid
from collections.abc import Container
from datetime import date

from unidecode import unidecode

from pjecz_hercules_cli_typer.core.exceptions import MyNotValidParamError

CLAVE_REGEXP = r"^[A-Z0-9_-]+$"
CURP_REGEXP = r"^[A-Z]{4}\d{6}[A-Z]{6}[A-Z0-9]{2}$"
EMAIL_REGEXP = r"^[\w.-]+@[\w.-]+\.\w+$"
EXPEDIENTE_REGEXP = r"^\d{1,5}/(19|20)\d{2}(-[A-Z0-9]+)?$"
CARACTERES_CONSERVADOS = "ÑÜ"


def safe_string(texto: str, max_len: int = 256) -> str:
    """Quitar espacios sobrantes, convertir a mayúsculas y quitar acentos, conservando Ñ y Ü"""
    texto = re.sub(r"\s+", " ", texto.strip()).upper()
    texto = "".join(c if c in CARACTERES_CONSERVADOS else unidecode(c) for c in texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto[:max_len].strip()


def safe_clave(clave: str, max_len: int = 16) -> str:
    """Validar una clave"""
    clave = safe_string(clave, max_len)
    if clave == "":
        return ""
    if re.match(CLAVE_REGEXP, clave) is None:
        raise MyNotValidParamError("La clave no es válida")
    return clave


def safe_curp(texto: str) -> str:
    """Validar un CURP"""
    texto = texto.strip().upper()
    if texto == "":
        return ""
    if re.match(CURP_REGEXP, texto) is None:
        raise MyNotValidParamError("El CURP no es válido")
    return texto


def safe_email(texto: str) -> str:
    """Validar un correo electrónico"""
    texto = texto.strip()
    if texto == "":
        return ""
    if re.match(EMAIL_REGEXP, texto) is None:
        raise MyNotValidParamError("El correo electrónico no es válido")
    return texto


def safe_expediente(expediente: str) -> str:
    """Validar un expediente y quitar los ceros a la izquierda del número"""
    expediente = safe_string(expediente)
    if expediente == "":
        return ""
    if re.match(EXPEDIENTE_REGEXP, expediente) is None:
        raise MyNotValidParamError("El expediente no es válido")
    numero, resto = expediente.split("/", 1)
    return f"{int(numero)}/{resto}"


def safe_fecha(fecha: str) -> date:
    """Validar que la fecha tenga el formato AAAA-MM-DD"""
    try:
        fecha_date = date.fromisoformat(fecha)
    except ValueError:
        raise MyNotValidParamError("La fecha no es válida")
    return fecha_date


def safe_nivel(nivel: int) -> None:
    """Validar que el nivel sea un entero comprendido entre 1 y 4"""
    if not isinstance(nivel, int) or isinstance(nivel, bool) or not (1 <= nivel <= 4):
        raise MyNotValidParamError("El nivel no es válido")


def safe_tipo_juicio(tipo_juicio: str, tipos_juicios: Container[str]) -> None:
    """Validar que el tipo de juicio sea uno de los permitidos"""
    if tipo_juicio not in tipos_juicios:
        raise MyNotValidParamError("El tipo de juicio no es válido")


def safe_opcion(valor: str, opciones: Container) -> str:
    """Validar que el valor sea una de las opciones del catálogo del modelo"""
    if valor == "":
        return ""
    if valor not in opciones:
        raise MyNotValidParamError("La opción no es válida")
    return valor


def safe_opcion_int(valor: int, opciones: Container) -> int:
    """Validar que el valor sea una de las opciones del catálogo del modelo"""
    if valor not in opciones:
        raise MyNotValidParamError("La opción no es válida")
    return valor


def safe_id(id_: int) -> int:
    """Validar que el id sea un entero positivo"""
    if not isinstance(id_, int) or isinstance(id_, bool) or id_ <= 0:
        raise MyNotValidParamError("El ID no es válido")
    return id_


def safe_uuid(texto: str) -> uuid.UUID:
    """Validar y convertir un UUID"""
    try:
        return uuid.UUID(texto.strip())
    except ValueError:
        raise MyNotValidParamError("El UUID no es válido")
