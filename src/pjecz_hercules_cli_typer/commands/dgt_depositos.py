"""
Digitalización Depósitos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_opcion, safe_string
from pjecz_hercules_cli_typer.models.dgt_depositos import DgtDepositos

app = Typer(help="Digitalización Depósitos")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    clave: str | None = None,
    descripcion: str | None = None,
    proposito: str | None = None,
):
    """Consultar depósitos de digitalización"""
    console = Console()
    console.print("Consultando depósitos de digitalización...")

    # Preparar tabla
    tabla = Table(title="Digitalización Depósitos")
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Descripción", header_style="green")
    tabla.add_column("Propósito", header_style="green")

    # Cláusulas where
    where_clauses = [DgtDepositos.estatus == "A"]
    if clave and (clave := safe_clave(clave, max_len=64)):
        where_clauses.append(DgtDepositos.clave == clave)
    if descripcion and (descripcion := safe_string(descripcion)):
        where_clauses.append(DgtDepositos.descripcion.like("%" + descripcion + "%"))
    if proposito and (proposito := safe_opcion(proposito, DgtDepositos.PROPOSITOS)):
        where_clauses.append(DgtDepositos.proposito == proposito)

    # Sentencia
    stmt = (
        select(DgtDepositos.clave, DgtDepositos.descripcion, DgtDepositos.proposito)
        .where(*where_clauses)
        .order_by(DgtDepositos.clave)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.clave, item.descripcion, item.proposito)
    console.print(tabla)
