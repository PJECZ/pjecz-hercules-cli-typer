"""
Digitalización Plataformas Endpoints
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_opcion
from pjecz_hercules_cli_typer.models.dgt_plataformas import DgtPlataforma
from pjecz_hercules_cli_typer.models.dgt_plataformas_endpoints import DgtPlataformaEndpoint

app = Typer(help="Digitalización Plataformas Endpoints")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    dgt_plataforma_clave: str | None = None,
    proposito: str | None = None,
    metodo: str | None = None,
):
    """Consultar endpoints de las plataformas"""
    console = Console()
    console.print("Consultando endpoints de las plataformas...")

    # Preparar tabla
    tabla = Table(title="Digitalización Plataformas Endpoints")
    tabla.add_column("Plataforma", header_style="green", no_wrap=True)
    tabla.add_column("Propósito", header_style="green")
    tabla.add_column("Método", header_style="green")
    tabla.add_column("Ruta", header_style="green")
    tabla.add_column("Descripción", header_style="green")

    # Cláusulas where
    where_clauses = [DgtPlataformaEndpoint.estatus == "A", DgtPlataforma.estatus == "A"]
    if dgt_plataforma_clave and (dgt_plataforma_clave := safe_clave(dgt_plataforma_clave, max_len=64)):
        where_clauses.append(DgtPlataforma.clave == dgt_plataforma_clave)
    if proposito and (proposito := safe_opcion(proposito, DgtPlataformaEndpoint.PROPOSITOS)):
        where_clauses.append(DgtPlataformaEndpoint.proposito == proposito)
    if metodo and (metodo := safe_opcion(metodo, DgtPlataformaEndpoint.METODOS)):
        where_clauses.append(DgtPlataformaEndpoint.metodo == metodo)

    # Sentencia
    stmt = (
        select(
            DgtPlataforma.clave.label("dgt_plataforma_clave"),
            DgtPlataformaEndpoint.proposito,
            DgtPlataformaEndpoint.metodo,
            DgtPlataformaEndpoint.ruta,
            DgtPlataformaEndpoint.descripcion,
        )
        .select_from(DgtPlataformaEndpoint)
        .join(DgtPlataforma, DgtPlataformaEndpoint.dgt_plataforma_id == DgtPlataforma.id)
        .where(*where_clauses)
        .order_by(DgtPlataforma.clave, DgtPlataformaEndpoint.ruta)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.dgt_plataforma_clave,
                item.proposito,
                item.metodo,
                item.ruta,
                item.descripcion,
            )
    console.print(tabla)
