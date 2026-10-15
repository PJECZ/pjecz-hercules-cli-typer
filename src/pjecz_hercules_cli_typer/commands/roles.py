"""
Roles
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.models.roles import Rol

app = Typer(help="Roles")


@app.command()
def consultar(offset: int = 0, limit: int = 25):
    """Consultar roles"""
    console = Console()
    console.print("Consultando roles...")
    tabla = Table(title="Roles")
    tabla.add_column("Nombre", header_style="green", no_wrap=True)
    stmt = (
        select(Rol.nombre)
        .where(Rol.estatus == "A")
        .order_by(Rol.nombre)
        .offset(offset)
        .limit(limit)
    )
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.nombre)
    console.print(tabla)
