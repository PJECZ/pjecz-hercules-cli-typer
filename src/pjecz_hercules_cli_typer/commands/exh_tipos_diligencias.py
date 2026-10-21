"""
Exhortos Tipos de Diligencias
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_string
from pjecz_hercules_cli_typer.models.exh_tipos_diligencias import ExhTipoDiligencia

app = Typer(help="Exhortos Tipos de Diligencias")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    clave: str | None = None,
    descripcion: str | None = None,
):
    """Consultar tipos de diligencias de exhortos"""
    console = Console()
    console.print("Consultando tipos de diligencias de exhortos...")

    # Preparar tabla
    tabla = Table(title="Exhortos Tipos de Diligencias")
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Descripción", header_style="green")

    # Cláusulas where
    where_clauses = [ExhTipoDiligencia.estatus == "A"]
    if clave and (clave := safe_clave(clave)):
        where_clauses.append(ExhTipoDiligencia.clave == clave)
    if descripcion and (descripcion := safe_string(descripcion)):
        where_clauses.append(ExhTipoDiligencia.descripcion.like("%" + descripcion + "%"))

    # Sentencia
    stmt = (
        select(ExhTipoDiligencia.clave, ExhTipoDiligencia.descripcion)
        .where(*where_clauses)
        .order_by(ExhTipoDiligencia.clave)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.clave, item.descripcion)
    console.print(tabla)
