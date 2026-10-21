"""
Digitalización Rutas
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave
from pjecz_hercules_cli_typer.models.dgt_depositos import DgtDepositos
from pjecz_hercules_cli_typer.models.dgt_rutas import DgtRuta
from pjecz_hercules_cli_typer.models.dgt_tipos import DgtTipo

app = Typer(help="Digitalización Rutas")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    dgt_deposito_clave: str | None = None,
    dgt_tipo_clave: str | None = None,
    clave: str | None = None,
    autoridad_clave: str | None = None,
):
    """Consultar rutas de digitalización"""
    console = Console()
    console.print("Consultando rutas de digitalización...")

    # Preparar tabla
    tabla = Table(title="Digitalización Rutas")
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Depósito", header_style="green", no_wrap=True)
    tabla.add_column("Tipo", header_style="green", no_wrap=True)
    tabla.add_column("Autoridad clave", header_style="green", no_wrap=True)
    tabla.add_column("Directorio", header_style="green")

    # Cláusulas where
    where_clauses = [DgtRuta.estatus == "A", DgtDepositos.estatus == "A", DgtTipo.estatus == "A"]
    if dgt_deposito_clave and (dgt_deposito_clave := safe_clave(dgt_deposito_clave, max_len=64)):
        where_clauses.append(DgtDepositos.clave == dgt_deposito_clave)
    if dgt_tipo_clave and (dgt_tipo_clave := safe_clave(dgt_tipo_clave, max_len=64)):
        where_clauses.append(DgtTipo.clave == dgt_tipo_clave)
    if clave and (clave := safe_clave(clave, max_len=64)):
        where_clauses.append(DgtRuta.clave == clave)
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        where_clauses.append(DgtRuta.autoridad_clave == autoridad_clave)

    # Sentencia
    stmt = (
        select(
            DgtRuta.clave,
            DgtDepositos.clave.label("dgt_deposito_clave"),
            DgtTipo.clave.label("dgt_tipo_clave"),
            DgtRuta.autoridad_clave,
            DgtRuta.directorio,
        )
        .select_from(DgtRuta)
        .join(DgtDepositos, DgtRuta.dgt_deposito_id == DgtDepositos.id)
        .join(DgtTipo, DgtRuta.dgt_tipo_id == DgtTipo.id)
        .where(*where_clauses)
        .order_by(DgtRuta.clave)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.clave,
                item.dgt_deposito_clave,
                item.dgt_tipo_clave,
                item.autoridad_clave,
                item.directorio,
            )
    console.print(tabla)
