"""
REDAM
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_fecha, safe_string
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.redams import Redam

app = Typer(help="REDAM")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    autoridad_clave: str | None = None,
    nombre: str | None = None,
    expediente: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
):
    """Consultar deudores alimentarios morosos"""
    console = Console()
    console.print("Consultando deudores alimentarios morosos...")

    # Preparar tabla
    tabla = Table(title="REDAM")
    tabla.add_column("Fecha", header_style="green", no_wrap=True)
    tabla.add_column("Autoridad", header_style="green", no_wrap=True)
    tabla.add_column("Expediente", header_style="green", no_wrap=True)
    tabla.add_column("Nombre", header_style="green")

    # Cláusulas where
    where_clauses = [Redam.estatus == "A", Autoridad.estatus == "A"]
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        where_clauses.append(Autoridad.clave == autoridad_clave)
    if nombre and (nombre := safe_string(nombre)):
        where_clauses.append(Redam.nombre.like("%" + nombre + "%"))
    if expediente and (expediente := safe_string(expediente)):
        where_clauses.append(Redam.expediente.like("%" + expediente + "%"))
    if fecha_desde and (desde := safe_fecha(fecha_desde)):
        where_clauses.append(Redam.fecha >= desde)
    if fecha_hasta and (hasta := safe_fecha(fecha_hasta)):
        where_clauses.append(Redam.fecha <= hasta)

    # Sentencia
    stmt = (
        select(
            Redam.fecha,
            Autoridad.clave.label("autoridad_clave"),
            Redam.expediente,
            Redam.nombre,
        )
        .select_from(Redam)
        .join(Autoridad, Redam.autoridad_id == Autoridad.id)
        .where(*where_clauses)
        .order_by(Redam.fecha.desc())
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.fecha.strftime("%Y-%m-%d"), item.autoridad_clave, item.expediente, item.nombre)
    console.print(tabla)
