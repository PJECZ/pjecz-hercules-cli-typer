"""
Domicilios
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_string
from pjecz_hercules_cli_typer.models.distritos import Distrito
from pjecz_hercules_cli_typer.models.domicilios import Domicilio

app = Typer(help="Domicilios")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    distrito_clave: str | None = None,
    edificio: str | None = None,
    municipio: str | None = None,
):
    """Consultar domicilios"""
    console = Console()
    console.print("Consultando domicilios...")

    # Preparar tabla
    tabla = Table(title="Domicilios")
    tabla.add_column("Edificio", header_style="green")
    tabla.add_column("Distrito", header_style="green", no_wrap=True)
    tabla.add_column("Municipio", header_style="green")
    tabla.add_column("Calle", header_style="green")
    tabla.add_column("Colonia", header_style="green")
    tabla.add_column("C.P.", header_style="green", no_wrap=True)

    # Cláusulas where
    where_clauses = [Domicilio.estatus == "A", Distrito.estatus == "A"]
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        where_clauses.append(Distrito.clave == distrito_clave)
    if edificio and (edificio := safe_string(edificio)):
        where_clauses.append(Domicilio.edificio.like("%" + edificio + "%"))
    if municipio and (municipio := safe_string(municipio)):
        where_clauses.append(Domicilio.municipio.like("%" + municipio + "%"))

    # Sentencia
    stmt = (
        select(
            Domicilio.edificio,
            Distrito.clave.label("distrito_clave"),
            Domicilio.municipio,
            Domicilio.calle,
            Domicilio.colonia,
            Domicilio.cp,
        )
        .select_from(Domicilio)
        .join(Distrito, Domicilio.distrito_id == Distrito.id)
        .where(*where_clauses)
        .order_by(Domicilio.edificio)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.edificio,
                item.distrito_clave,
                item.municipio,
                item.calle,
                item.colonia,
                str(item.cp),
            )
    console.print(tabla)
