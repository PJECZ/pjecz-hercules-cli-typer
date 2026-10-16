"""
Edictos
"""

from datetime import date

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Exit, Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.safe_string import safe_clave, safe_string
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.edictos import Edicto

app = Typer(help="Edictos")


def _validar_fecha(fecha: str) -> date:
    """Validar que la fecha tenga el formato AAAA-MM-DD"""
    try:
        return date.fromisoformat(fecha)
    except ValueError:
        raise Exit(1)


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    autoridad_clave: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    expediente: str | None = None,
    numero_publicacion: str | None = None,
    descripcion: str | None = None,
):
    """Consultar edictos"""
    console = Console()
    console.print("Consultando edictos...")

    # Preparar tabla
    tabla = Table(title="Edictos")
    tabla.add_column("Fecha", header_style="green", no_wrap=True)
    tabla.add_column("Autoridad", header_style="green", no_wrap=True)
    tabla.add_column("Expediente", header_style="green", no_wrap=True)
    tabla.add_column("No. publicación", header_style="green", no_wrap=True)
    tabla.add_column("Descripción", header_style="green")
    tabla.add_column("D. ausencia", header_style="green")

    # Cláusulas where
    where_clauses = [Edicto.estatus == "A", Autoridad.estatus == "A"]
    autoridad_clave = safe_clave(autoridad_clave)
    if autoridad_clave:
        where_clauses.append(Autoridad.clave == autoridad_clave)
    if fecha_desde:
        where_clauses.append(Edicto.fecha >= _validar_fecha(fecha_desde))
    if fecha_hasta:
        where_clauses.append(Edicto.fecha <= _validar_fecha(fecha_hasta))
    expediente = safe_string(expediente)
    if expediente:
        where_clauses.append(Edicto.expediente.like("%" + expediente + "%"))
    numero_publicacion = safe_string(numero_publicacion)
    if numero_publicacion:
        where_clauses.append(Edicto.numero_publicacion.like("%" + numero_publicacion + "%"))
    descripcion = safe_string(descripcion, save_enie=True)
    if descripcion:
        where_clauses.append(Edicto.descripcion.like("%" + descripcion + "%"))

    # Sentencia
    stmt = (
        select(
            Edicto.fecha,
            Autoridad.clave.label("autoridad_clave"),
            Edicto.expediente,
            Edicto.numero_publicacion,
            Edicto.descripcion,
            Edicto.es_declaracion_de_ausencia,
        )
        .select_from(Edicto)
        .join(Autoridad, Edicto.autoridad_id == Autoridad.id)
        .where(*where_clauses)
        .order_by(Edicto.fecha.desc(), Autoridad.clave)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.fecha.strftime("%Y-%m-%d"),
                item.autoridad_clave,
                item.expediente,
                item.numero_publicacion,
                item.descripcion,
                "Sí" if item.es_declaracion_de_ausencia else "No",
            )
    console.print(tabla)
