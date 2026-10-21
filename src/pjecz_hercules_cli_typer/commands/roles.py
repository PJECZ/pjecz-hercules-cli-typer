"""
Roles
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_string
from pjecz_hercules_cli_typer.models.roles import Rol

app = Typer(help="Roles")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    nombre: str | None = None,
):
    """Consultar roles"""
    console = Console()
    console.print("Consultando roles...")

    # Preparar tabla
    tabla = Table(title="Roles")
    tabla.add_column("Nombre", header_style="green", no_wrap=True)

    # Cláusulas where
    where_clauses = [Rol.estatus == "A"]
    nombre = safe_string(nombre, save_enie=True)
    if nombre:
        where_clauses.append(Rol.nombre.like("%" + nombre + "%"))

    # Sentencia
    stmt = (
        select(Rol.nombre)
        .where(*where_clauses)
        .order_by(Rol.nombre)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.nombre)
    console.print(tabla)
