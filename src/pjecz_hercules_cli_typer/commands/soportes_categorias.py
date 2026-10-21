"""
Soportes Categorías
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_opcion, safe_string
from pjecz_hercules_cli_typer.models.soportes_categorias import SoporteCategoria

app = Typer(help="Soportes Categorías")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    nombre: str | None = None,
    departamento: str | None = None,
):
    """Consultar categorías de soportes"""
    console = Console()
    console.print("Consultando categorías de soportes...")

    # Preparar tabla
    tabla = Table(title="Soportes Categorías")
    tabla.add_column("Nombre", header_style="green")
    tabla.add_column("Departamento", header_style="green")

    # Cláusulas where
    where_clauses = [SoporteCategoria.estatus == "A"]
    if nombre and (nombre := safe_string(nombre)):
        where_clauses.append(SoporteCategoria.nombre.like("%" + nombre + "%"))
    if departamento and (departamento := safe_opcion(departamento, SoporteCategoria.DEPARTAMENTOS)):
        where_clauses.append(SoporteCategoria.departamento == departamento)

    # Sentencia
    stmt = (
        select(SoporteCategoria.nombre, SoporteCategoria.departamento)
        .where(*where_clauses)
        .order_by(SoporteCategoria.nombre)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.nombre, item.departamento or "")
    console.print(tabla)
