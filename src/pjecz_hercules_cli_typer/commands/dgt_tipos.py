"""
Digitalización Tipos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_string
from pjecz_hercules_cli_typer.models.dgt_tipos import DgtTipo

app = Typer(help="Digitalización Tipos")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    clave: str | None = None,
    descripcion: str | None = None,
):
    """Consultar tipos de digitalización"""
    console = Console()
    console.print("Consultando tipos de digitalización...")

    # Preparar tabla
    tabla = Table(title="Digitalización Tipos")
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Descripción", header_style="green")

    # Cláusulas where
    where_clauses = [DgtTipo.estatus == "A"]
    if clave and (clave := safe_clave(clave, max_len=64)):
        where_clauses.append(DgtTipo.clave == clave)
    if descripcion and (descripcion := safe_string(descripcion)):
        where_clauses.append(DgtTipo.descripcion.like("%" + descripcion + "%"))

    # Sentencia
    stmt = select(DgtTipo.clave, DgtTipo.descripcion).where(*where_clauses).order_by(DgtTipo.clave).offset(offset).limit(limit)

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.clave, item.descripcion)
    console.print(tabla)
