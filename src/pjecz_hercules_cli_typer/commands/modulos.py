"""
Módulos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.models.modulos import Modulo

app = Typer(help="Módulos")


@app.command()
def consultar(offset: int = 0, limit: int = 50):
    """Consultar módulos"""
    console = Console()
    console.print("Consultando módulos...")
    tabla = Table(title="Módulos")
    tabla.add_column("Nombre", header_style="green", no_wrap=True)
    tabla.add_column("Nombre corto", header_style="green")
    tabla.add_column("Icono", header_style="green")
    tabla.add_column("Ruta", header_style="green")
    tabla.add_column("En navegación", header_style="green")
    stmt = (
        select(
            Modulo.nombre,
            Modulo.nombre_corto,
            Modulo.icono,
            Modulo.ruta,
            Modulo.en_navegacion,
        )
        .where(Modulo.estatus == "A")
        .order_by(Modulo.nombre)
        .offset(offset)
        .limit(limit)
    )
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.nombre, item.nombre_corto, item.icono, item.ruta, "Sí" if item.en_navegacion else "")
    console.print(tabla)
