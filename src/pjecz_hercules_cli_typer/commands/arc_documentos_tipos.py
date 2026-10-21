"""
Archivo Documentos Tipos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_string
from pjecz_hercules_cli_typer.models.arc_documentos_tipos import ArcDocumentoTipo

app = Typer(help="Archivo Documentos Tipos")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    nombre: str | None = None,
):
    """Consultar tipos de documentos del archivo"""
    console = Console()
    console.print("Consultando tipos de documentos del archivo...")

    # Preparar tabla
    tabla = Table(title="Archivo Documentos Tipos")
    tabla.add_column("Nombre", header_style="green")

    # Cláusulas where
    where_clauses = [ArcDocumentoTipo.estatus == "A"]
    if nombre and (nombre := safe_string(nombre)):
        where_clauses.append(ArcDocumentoTipo.nombre.like("%" + nombre + "%"))

    # Sentencia
    stmt = select(ArcDocumentoTipo.nombre).where(*where_clauses).order_by(ArcDocumentoTipo.nombre).offset(offset).limit(limit)

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.nombre)
    console.print(tabla)
