"""
Permisos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.models.modulos import Modulo
from pjecz_hercules_cli_typer.models.permisos import Permiso
from pjecz_hercules_cli_typer.models.roles import Rol

app = Typer(help="Permisos")


@app.command()
def consultar(offset: int = 0, limit: int = 25):
    """Consultar permisos"""
    console = Console()
    console.print("Consultando permisos...")
    tabla = Table(title="Permisos")
    tabla.add_column("Rol", header_style="green")
    tabla.add_column("Módulo", header_style="green")
    tabla.add_column("Nivel", header_style="green")
    stmt = (
        select(
            Rol.nombre.label("rol_nombre"),
            Modulo.nombre.label("modulo_nombre"),
            Permiso.nivel,
        )
        .select_from(Permiso)
        .join(Modulo)
        .join(Rol)
        .where(Permiso.estatus == "A")
        .where(Modulo.estatus == "A")
        .where(Rol.estatus == "A")
        .order_by(Rol.nombre, Modulo.nombre, Permiso.nivel)
        .offset(offset)
        .limit(limit)
    )
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.rol_nombre, item.modulo_nombre, str(item.nivel))
    console.print(tabla)
