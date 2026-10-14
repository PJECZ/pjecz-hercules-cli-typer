"""
Usuarios
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.distritos import Distrito
from pjecz_hercules_cli_typer.models.usuarios import Usuario

app = Typer(help="Usuarios")


@app.command()
def consultar(offset: int = 0, limit: int = 50):
    """Consultar usuarios"""
    console = Console()
    console.print("Consultando usuarios...")
    tabla = Table(title="Usuarios")
    tabla.add_column("Email", header_style="green", no_wrap=True)
    tabla.add_column("Nombres", header_style="green")
    tabla.add_column("A. Paterno", header_style="green")
    tabla.add_column("A. Materno", header_style="green")
    tabla.add_column("CURP", header_style="green")
    tabla.add_column("Distrito", header_style="green")
    tabla.add_column("Autoridad", header_style="green")
    tabla.add_column("Puesto", header_style="green")
    stmt = (
        select(
            Usuario.email,
            Usuario.nombres,
            Usuario.apellido_paterno,
            Usuario.apellido_materno,
            Usuario.curp,
            Distrito.clave.label("distrito_clave"),
            Autoridad.clave.label("autoridad_clave"),
            Usuario.puesto,
        )
        .select_from(Usuario)
        .join(Autoridad, Usuario.autoridad_id == Autoridad.id)
        .join(Distrito, Autoridad.distrito_id == Distrito.id)
        .where(Usuario.estatus == "A")
        .order_by(Usuario.email)
        .offset(offset)
        .limit(limit)
    )
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.email,
                item.nombres,
                item.apellido_paterno,
                item.apellido_materno,
                item.curp,
                item.distrito_clave,
                item.autoridad_clave,
                item.puesto,
            )
    console.print(tabla)
