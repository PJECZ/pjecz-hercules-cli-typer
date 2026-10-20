"""
Permisos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.safe_string import safe_string
from pjecz_hercules_cli_typer.core.validations import validar_nivel
from pjecz_hercules_cli_typer.models.modulos import Modulo
from pjecz_hercules_cli_typer.models.permisos import Permiso
from pjecz_hercules_cli_typer.models.roles import Rol

app = Typer(help="Permisos")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    rol_nombre: str | None = None,
    modulo_nombre: str | None = None,
    nivel: int | None = None,
):
    """Consultar permisos"""
    console = Console()
    console.print("Consultando permisos...")

    # Validar el filtro por nivel (valores permitidos: 1 a 4)
    if nivel is not None:
        validar_nivel(nivel)

    # Preparar tabla
    tabla = Table(title="Permisos")
    tabla.add_column("Rol", header_style="green")
    tabla.add_column("Módulo", header_style="green")
    tabla.add_column("Nivel", header_style="green")

    # Cláusulas where
    where_clauses = [Permiso.estatus == "A", Modulo.estatus == "A", Rol.estatus == "A"]
    rol_nombre = safe_string(rol_nombre)
    if rol_nombre:
        where_clauses.append(Rol.nombre.like("%" + rol_nombre + "%"))
    modulo_nombre = safe_string(modulo_nombre)
    if modulo_nombre:
        where_clauses.append(Modulo.nombre.like("%" + modulo_nombre + "%"))
    if nivel is not None:
        where_clauses.append(Permiso.nivel == nivel)

    # Sentencia
    stmt = (
        select(
            Rol.nombre.label("rol_nombre"),
            Modulo.nombre.label("modulo_nombre"),
            Permiso.nivel,
        )
        .select_from(Permiso)
        .join(Modulo)
        .join(Rol)
        .where(*where_clauses)
        .order_by(Rol.nombre, Modulo.nombre, Permiso.nivel)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.rol_nombre, item.modulo_nombre, str(item.nivel))
    console.print(tabla)
