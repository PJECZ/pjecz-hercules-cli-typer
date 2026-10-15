"""
Módulos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.safe_string import safe_string
from pjecz_hercules_cli_typer.models.modulos import Modulo

app = Typer(help="Módulos")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    nombre: str | None = None,
    en_navegacion: bool | None = None,
):
    """Consultar módulos"""
    console = Console()
    console.print("Consultando módulos...")

    # Preparar tabla
    tabla = Table(title="Módulos")
    tabla.add_column("Nombre", header_style="green", no_wrap=True)
    tabla.add_column("Nombre corto", header_style="green")
    tabla.add_column("Icono", header_style="green")
    tabla.add_column("Ruta", header_style="green")
    tabla.add_column("En navegación", header_style="green")

    # Cláusulas where
    where_clauses = [Modulo.estatus == "A"]
    nombre = safe_string(nombre, save_enie=True)
    if nombre:
        where_clauses.append(Modulo.nombre.like("%" + nombre + "%"))
    if en_navegacion is not None:
        where_clauses.append(Modulo.en_navegacion == en_navegacion)

    # Sentencia
    stmt = (
        select(
            Modulo.nombre,
            Modulo.nombre_corto,
            Modulo.icono,
            Modulo.ruta,
            Modulo.en_navegacion,
        )
        .where(*where_clauses)
        .order_by(Modulo.nombre)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.nombre, item.nombre_corto, item.icono, item.ruta, "Sí" if item.en_navegacion else "")
    console.print(tabla)
