"""
Materias Tipos de Juicios
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_string
from pjecz_hercules_cli_typer.models.materias import Materia
from pjecz_hercules_cli_typer.models.materias_tipos_juicios import MateriaTipoJuicio

app = Typer(help="Materias Tipos de Juicios")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    materia_clave: str | None = None,
    descripcion: str | None = None,
):
    """Consultar materias tipos de juicios"""
    console = Console()
    console.print("Consultando materias tipos de juicios...")

    # Preparar tabla
    tabla = Table(title="Materias Tipos de Juicios")
    tabla.add_column("Materia", header_style="green", no_wrap=True)
    tabla.add_column("Materia nombre", header_style="green")
    tabla.add_column("Descripción", header_style="green")

    # Cláusulas where
    where_clauses = [MateriaTipoJuicio.estatus == "A", Materia.estatus == "A"]
    if materia_clave and (materia_clave := safe_clave(materia_clave)):
        where_clauses.append(Materia.clave == materia_clave)
    if descripcion and (descripcion := safe_string(descripcion)):
        where_clauses.append(MateriaTipoJuicio.descripcion.like("%" + descripcion + "%"))

    # Sentencia
    stmt = (
        select(
            Materia.clave.label("materia_clave"),
            Materia.nombre.label("materia_nombre"),
            MateriaTipoJuicio.descripcion,
        )
        .select_from(MateriaTipoJuicio)
        .join(Materia, MateriaTipoJuicio.materia_id == Materia.id)
        .where(*where_clauses)
        .order_by(Materia.clave, MateriaTipoJuicio.descripcion)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.materia_clave,
                item.materia_nombre,
                item.descripcion,
            )
    console.print(tabla)
