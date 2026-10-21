"""
Digitalización Plataformas
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_string
from pjecz_hercules_cli_typer.models.dgt_plataformas import DgtPlataforma

app = Typer(help="Digitalización Plataformas")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    clave: str | None = None,
    descripcion: str | None = None,
):
    """Consultar plataformas de digitalización"""
    console = Console()
    console.print("Consultando plataformas de digitalización...")

    # Preparar tabla
    tabla = Table(title="Digitalización Plataformas")
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Descripción", header_style="green")

    # Cláusulas where
    where_clauses = [DgtPlataforma.estatus == "A"]
    if clave and (clave := safe_clave(clave, max_len=64)):
        where_clauses.append(DgtPlataforma.clave == clave)
    if descripcion and (descripcion := safe_string(descripcion)):
        where_clauses.append(DgtPlataforma.descripcion.like("%" + descripcion + "%"))

    # Sentencia
    stmt = (
        select(DgtPlataforma.clave, DgtPlataforma.descripcion)
        .where(*where_clauses)
        .order_by(DgtPlataforma.clave)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.clave, item.descripcion)
    console.print(tabla)
