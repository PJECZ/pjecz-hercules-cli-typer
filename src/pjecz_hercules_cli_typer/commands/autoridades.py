"""
Autoridades
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.models.autoridades import Autoridad

app = Typer(help="Autoridades")


@app.command()
def consultar(offset: int = 0, limit: int = 100):
    """Consultar autoridades"""
    console = Console()
    console.print("Consultando autoridades...")
    tabla = Table(title="Autoridades")
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Descripción corta", header_style="green")
    stmt = (
        select(
            Autoridad.clave,
            Autoridad.descripcion_corta,
        )
        .where(Autoridad.estatus == "A")
        .order_by(Autoridad.clave)
        .offset(offset)
        .limit(limit)
    )
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.clave, item.descripcion_corta)
    console.print(tabla)
