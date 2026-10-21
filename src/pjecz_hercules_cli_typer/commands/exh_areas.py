"""
Exhortos Áreas
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_string
from pjecz_hercules_cli_typer.models.exh_areas import ExhArea

app = Typer(help="Exhortos Áreas")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    clave: str | None = None,
    nombre: str | None = None,
):
    """Consultar áreas de exhortos"""
    console = Console()
    console.print("Consultando áreas de exhortos...")

    # Preparar tabla
    tabla = Table(title="Exhortos Áreas")
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Nombre", header_style="green")

    # Cláusulas where
    where_clauses = [ExhArea.estatus == "A"]
    if clave and (clave := safe_clave(clave)):
        where_clauses.append(ExhArea.clave == clave)
    if nombre and (nombre := safe_string(nombre)):
        where_clauses.append(ExhArea.nombre.like("%" + nombre + "%"))

    # Sentencia
    stmt = select(ExhArea.clave, ExhArea.nombre).where(*where_clauses).order_by(ExhArea.clave).offset(offset).limit(limit)

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.clave, item.nombre)
    console.print(tabla)
