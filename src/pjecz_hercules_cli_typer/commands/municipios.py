"""
Municipios
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_string
from pjecz_hercules_cli_typer.models.estados import Estado
from pjecz_hercules_cli_typer.models.municipios import Municipio

app = Typer(help="Municipios")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    estado_clave: str | None = None,
    clave: str | None = None,
    nombre: str | None = None,
):
    """Consultar municipios"""
    console = Console()
    console.print("Consultando municipios...")

    # Preparar tabla
    tabla = Table(title="Municipios")
    tabla.add_column("Estado", header_style="green", no_wrap=True)
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Nombre", header_style="green")

    # Cláusulas where
    where_clauses = [Municipio.estatus == "A", Estado.estatus == "A"]
    if estado_clave and (estado_clave := safe_clave(estado_clave)):
        where_clauses.append(Estado.clave == estado_clave)
    if clave and (clave := safe_clave(clave)):
        where_clauses.append(Municipio.clave == clave)
    if nombre and (nombre := safe_string(nombre)):
        where_clauses.append(Municipio.nombre.like("%" + nombre + "%"))

    # Sentencia
    stmt = (
        select(
            Estado.clave.label("estado_clave"),
            Municipio.clave,
            Municipio.nombre,
        )
        .select_from(Municipio)
        .join(Estado, Municipio.estado_id == Estado.id)
        .where(*where_clauses)
        .order_by(Estado.clave, Municipio.clave)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.estado_clave, item.clave, item.nombre)
    console.print(tabla)
