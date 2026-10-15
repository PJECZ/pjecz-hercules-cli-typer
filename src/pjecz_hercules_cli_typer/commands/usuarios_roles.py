"""
Usuarios-Roles
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.models.roles import Rol
from pjecz_hercules_cli_typer.models.usuarios import Usuario
from pjecz_hercules_cli_typer.models.usuarios_roles import UsuarioRol

app = Typer(help="Usuarios-Roles")


@app.command()
def consultar(offset: int = 0, limit: int = 25):
    """Consultar usuarios-roles"""
    console = Console()
    console.print("Consultando usuarios-roles...")
    tabla = Table(title="Usuarios-Roles")
    tabla.add_column("Usuario", header_style="green", no_wrap=True)
    tabla.add_column("Rol", header_style="green", no_wrap=True)
    stmt = (
        select(
            Usuario.email.label("usuario_email"),
            Rol.nombre.label("rol_nombre"),
        )
        .select_from(UsuarioRol)
        .join(Usuario)
        .join(Rol)
        .where(UsuarioRol.estatus == "A")
        .where(Usuario.estatus == "A")
        .where(Rol.estatus == "A")
        .order_by(Usuario.email, Rol.nombre)
        .offset(offset)
        .limit(limit)
    )
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.usuario_email, item.rol_nombre)
    console.print(tabla)
