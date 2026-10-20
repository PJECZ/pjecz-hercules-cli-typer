"""
Models

Importa todos los modelos para que SQLAlchemy pueda resolver las relaciones declaradas con nombres de clase.
"""

from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.distritos import Distrito
from pjecz_hercules_cli_typer.models.edictos import Edicto
from pjecz_hercules_cli_typer.models.glosas import Glosa
from pjecz_hercules_cli_typer.models.listas_de_acuerdos import ListaDeAcuerdo
from pjecz_hercules_cli_typer.models.materias import Materia
from pjecz_hercules_cli_typer.models.materias_tipos_juicios import MateriaTipoJuicio
from pjecz_hercules_cli_typer.models.modulos import Modulo
from pjecz_hercules_cli_typer.models.ofi_documentos import OfiDocumento
from pjecz_hercules_cli_typer.models.ofi_documentos_adjuntos import OfiDocumentoAdjunto
from pjecz_hercules_cli_typer.models.ofi_documentos_destinatarios import OfiDocumentoDestinatario
from pjecz_hercules_cli_typer.models.permisos import Permiso
from pjecz_hercules_cli_typer.models.roles import Rol
from pjecz_hercules_cli_typer.models.sentencias import Sentencia
from pjecz_hercules_cli_typer.models.usuarios import Usuario
from pjecz_hercules_cli_typer.models.usuarios_roles import UsuarioRol

__all__ = [
    "Autoridad",
    "Distrito",
    "Edicto",
    "Glosa",
    "ListaDeAcuerdo",
    "Materia",
    "MateriaTipoJuicio",
    "Modulo",
    "OfiDocumento",
    "OfiDocumentoAdjunto",
    "OfiDocumentoDestinatario",
    "Permiso",
    "Rol",
    "Sentencia",
    "Usuario",
    "UsuarioRol",
]
