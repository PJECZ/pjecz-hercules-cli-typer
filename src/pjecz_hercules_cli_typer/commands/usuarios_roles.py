"""
Usuarios-Roles
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_email, safe_string
from pjecz_hercules_cli_typer.models.roles import Rol
from pjecz_hercules_cli_typer.models.usuarios import Usuario
from pjecz_hercules_cli_typer.models.usuarios_roles import UsuarioRol

app = Typer(help="Usuarios-Roles")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    email: str | None = None,
    rol_nombre: str | None = None,
):
    """Consultar usuarios-roles"""
    console = Console()
    console.print("Consultando usuarios-roles...")

    # Preparar tabla
    tabla = Table(title="Usuarios-Roles")
    tabla.add_column("Usuario", header_style="green", no_wrap=True)
    tabla.add_column("Rol", header_style="green", no_wrap=True)

    # Cláusulas where
    where_clauses = [UsuarioRol.estatus == "A", Usuario.estatus == "A", Rol.estatus == "A"]
    email = safe_email(email, search_fragment=True)
    if email:
        where_clauses.append(Usuario.email.like("%" + email + "%"))
    rol_nombre = safe_string(rol_nombre)
    if rol_nombre:
        where_clauses.append(Rol.nombre.like("%" + rol_nombre + "%"))

    # Sentencia
    stmt = (
        select(
            Usuario.email.label("usuario_email"),
            Rol.nombre.label("rol_nombre"),
        )
        .select_from(UsuarioRol)
        .join(Usuario)
        .join(Rol)
        .where(*where_clauses)
        .order_by(Usuario.email, Rol.nombre)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.usuario_email, item.rol_nombre)
    console.print(tabla)
