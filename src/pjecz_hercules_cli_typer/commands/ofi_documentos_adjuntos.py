"""
Oficios Documentos Adjuntos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_string, safe_uuid
from pjecz_hercules_cli_typer.models.ofi_documentos import OfiDocumento
from pjecz_hercules_cli_typer.models.ofi_documentos_adjuntos import OfiDocumentoAdjunto

app = Typer(help="Oficios Documentos Adjuntos")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    ofi_documento_id: str | None = None,
    descripcion: str | None = None,
):
    """Consultar adjuntos de oficios documentos"""
    console = Console()
    console.print("Consultando adjuntos de oficios documentos...")

    # Preparar tabla
    tabla = Table(title="Oficios Documentos Adjuntos")
    tabla.add_column("Oficio ID", header_style="green", no_wrap=True)
    tabla.add_column("Descripción", header_style="green")
    tabla.add_column("Archivo", header_style="green")

    # Cláusulas where
    where_clauses = [OfiDocumentoAdjunto.estatus == "A", OfiDocumento.estatus == "A"]
    if ofi_documento_id and (ofi_documento_uuid := safe_uuid(ofi_documento_id)):
        where_clauses.append(OfiDocumentoAdjunto.ofi_documento_id == ofi_documento_uuid)
    if descripcion and (descripcion := safe_string(descripcion)):
        where_clauses.append(OfiDocumentoAdjunto.descripcion.like("%" + descripcion + "%"))

    # Sentencia
    stmt = (
        select(
            OfiDocumentoAdjunto.ofi_documento_id,
            OfiDocumentoAdjunto.descripcion,
            OfiDocumentoAdjunto.archivo,
        )
        .select_from(OfiDocumentoAdjunto)
        .join(OfiDocumento, OfiDocumentoAdjunto.ofi_documento_id == OfiDocumento.id)
        .where(*where_clauses)
        .order_by(OfiDocumentoAdjunto.descripcion)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(str(item.ofi_documento_id), item.descripcion, item.archivo)
    console.print(tabla)
