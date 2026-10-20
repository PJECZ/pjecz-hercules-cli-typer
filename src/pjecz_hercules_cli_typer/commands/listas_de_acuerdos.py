"""
Listas de Acuerdos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.safe_string import safe_clave, safe_string
from pjecz_hercules_cli_typer.core.validations import safe_fecha
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.listas_de_acuerdos import ListaDeAcuerdo

app = Typer(help="Listas de Acuerdos")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    autoridad_clave: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    descripcion: str | None = None,
):
    """Consultar listas de acuerdos"""
    console = Console()
    console.print("Consultando listas de acuerdos...")

    # Preparar tabla
    tabla = Table(title="Listas de Acuerdos")
    tabla.add_column("Fecha", header_style="green", no_wrap=True)
    tabla.add_column("Autoridad", header_style="green", no_wrap=True)
    tabla.add_column("Descripción", header_style="green")

    # Cláusulas where
    where_clauses = [ListaDeAcuerdo.estatus == "A", Autoridad.estatus == "A"]
    autoridad_clave = safe_clave(autoridad_clave)
    if autoridad_clave:
        where_clauses.append(Autoridad.clave == autoridad_clave)
    if fecha_desde:
        where_clauses.append(ListaDeAcuerdo.fecha >= safe_fecha(fecha_desde))
    if fecha_hasta:
        where_clauses.append(ListaDeAcuerdo.fecha <= safe_fecha(fecha_hasta))
    descripcion = safe_string(descripcion, save_enie=True)
    if descripcion:
        where_clauses.append(ListaDeAcuerdo.descripcion.like("%" + descripcion + "%"))

    # Sentencia
    stmt = (
        select(
            ListaDeAcuerdo.fecha,
            Autoridad.clave.label("autoridad_clave"),
            ListaDeAcuerdo.descripcion,
        )
        .select_from(ListaDeAcuerdo)
        .join(Autoridad, ListaDeAcuerdo.autoridad_id == Autoridad.id)
        .where(*where_clauses)
        .order_by(ListaDeAcuerdo.fecha.desc(), Autoridad.clave)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.fecha.strftime("%Y-%m-%d"),
                item.autoridad_clave,
                item.descripcion,
            )
    console.print(tabla)
