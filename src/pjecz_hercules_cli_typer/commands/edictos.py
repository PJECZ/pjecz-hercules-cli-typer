"""
Edictos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_expediente, safe_fecha, safe_string
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.edictos import Edicto

app = Typer(help="Edictos")


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
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        where_clauses.append(Autoridad.clave == autoridad_clave)
    if fecha_desde and (desde := safe_fecha(fecha_desde)):
        where_clauses.append(Edicto.fecha >= desde)
    if fecha_hasta and (hasta := safe_fecha(fecha_hasta)):
        where_clauses.append(Edicto.fecha <= hasta)
    if expediente and (expediente := safe_expediente(expediente)):
        where_clauses.append(Edicto.expediente == expediente)
    if numero_publicacion and (numero_publicacion := safe_string(numero_publicacion)):
        where_clauses.append(Edicto.numero_publicacion.like("%" + numero_publicacion + "%"))
    if descripcion and (descripcion := safe_string(descripcion)):
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
