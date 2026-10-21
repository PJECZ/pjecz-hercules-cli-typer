"""
Oficios Documentos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_email, safe_string
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.ofi_documentos import OfiDocumento
from pjecz_hercules_cli_typer.models.usuarios import Usuario

app = Typer(help="Oficios Documentos")

DESCRIPCION_MAX_LEN = 48


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    autoridad_clave: str | None = None,
    usuario_email: str | None = None,
    descripcion: str | None = None,
):
    """Consultar oficios documentos"""
    console = Console()
    console.print("Consultando oficios documentos...")

    # Preparar tabla
    tabla = Table(title="Oficios Documentos")
    tabla.add_column("ID", header_style="green", no_wrap=True)
    tabla.add_column("Autoridad", header_style="green", no_wrap=True)
    tabla.add_column("Usuario", header_style="green", no_wrap=True)
    tabla.add_column("Folio", header_style="green", no_wrap=True)
    tabla.add_column("Descripción", header_style="green")
    tabla.add_column("Estado", header_style="green")
    tabla.add_column("Archivado", header_style="green")
    tabla.add_column("Cancelado", header_style="green")

    # Cláusulas where
    where_clauses = [OfiDocumento.estatus == "A", Usuario.estatus == "A", Autoridad.estatus == "A"]
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        where_clauses.append(Autoridad.clave == autoridad_clave)
    if usuario_email and (usuario_email := safe_email(usuario_email)):
        where_clauses.append(Usuario.email == usuario_email)
    if descripcion and (descripcion := safe_string(descripcion)):
        where_clauses.append(OfiDocumento.descripcion.like("%" + descripcion + "%"))

    # Sentencia
    stmt = (
        select(
            OfiDocumento.id,
            Autoridad.clave.label("autoridad_clave"),
            Usuario.email.label("usuario_email"),
            OfiDocumento.folio,
            OfiDocumento.descripcion,
            OfiDocumento.estado,
            OfiDocumento.esta_archivado,
            OfiDocumento.esta_cancelado,
        )
        .select_from(OfiDocumento)
        .join(Usuario, OfiDocumento.usuario_id == Usuario.id)
        .join(Autoridad, Usuario.autoridad_id == Autoridad.id)
        .where(*where_clauses)
        .order_by(OfiDocumento.creado.desc())
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            descripcion_corta = item.descripcion
            if len(descripcion_corta) > DESCRIPCION_MAX_LEN:
                descripcion_corta = descripcion_corta[: DESCRIPCION_MAX_LEN - 3] + "..."
            tabla.add_row(
                str(item.id),
                item.autoridad_clave,
                item.usuario_email,
                item.folio or "",
                descripcion_corta,
                item.estado,
                "Sí" if item.esta_archivado else "No",
                "Sí" if item.esta_cancelado else "No",
            )
    console.print(tabla)
