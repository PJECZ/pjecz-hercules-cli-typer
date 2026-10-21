"""
Digitalización Entregas
"""

from datetime import timedelta

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_expediente, safe_fecha, safe_string
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.dgt_entregas import DgtEntrega
from pjecz_hercules_cli_typer.models.dgt_rutas import DgtRuta

app = Typer(help="Digitalización Entregas")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    autoridad_clave: str | None = None,
    dgt_ruta_clave: str | None = None,
    expediente: str | None = None,
    archivo_nombre: str | None = None,
    ultimo_evento: str | None = None,
    es_anomalo: bool | None = None,
    ultimo_evento_creado_desde: str | None = None,
    ultimo_evento_creado_hasta: str | None = None,
):
    """Consultar entregas de digitalización"""
    console = Console()
    console.print("Consultando entregas de digitalización...")

    # Preparar tabla
    tabla = Table(title="Digitalización Entregas")
    tabla.add_column("Autoridad", header_style="green", no_wrap=True)
    tabla.add_column("Ruta", header_style="green", no_wrap=True)
    tabla.add_column("Expediente", header_style="green", no_wrap=True)
    tabla.add_column("Archivo", header_style="green")
    tabla.add_column("Último evento", header_style="green")
    tabla.add_column("Fecha evento", header_style="green", no_wrap=True)
    tabla.add_column("Anómalo", header_style="green")

    # Cláusulas where
    where_clauses = [DgtEntrega.estatus == "A", Autoridad.estatus == "A", DgtRuta.estatus == "A"]
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        where_clauses.append(Autoridad.clave == autoridad_clave)
    if dgt_ruta_clave and (dgt_ruta_clave := safe_clave(dgt_ruta_clave, max_len=64)):
        where_clauses.append(DgtRuta.clave == dgt_ruta_clave)
    if expediente and (expediente := safe_expediente(expediente)):
        where_clauses.append(DgtEntrega.expediente == expediente)
    if archivo_nombre and (archivo_nombre := safe_string(archivo_nombre)):
        where_clauses.append(DgtEntrega.archivo_nombre.like("%" + archivo_nombre + "%"))
    if ultimo_evento and (ultimo_evento := safe_string(ultimo_evento)):
        where_clauses.append(DgtEntrega.ultimo_evento == ultimo_evento)
    if es_anomalo is not None:
        where_clauses.append(DgtEntrega.es_anomalo == es_anomalo)
    if ultimo_evento_creado_desde and (desde := safe_fecha(ultimo_evento_creado_desde)):
        where_clauses.append(DgtEntrega.ultimo_evento_creado >= desde)
    if ultimo_evento_creado_hasta and (hasta := safe_fecha(ultimo_evento_creado_hasta)):
        where_clauses.append(DgtEntrega.ultimo_evento_creado < hasta + timedelta(days=1))

    # Sentencia
    stmt = (
        select(
            Autoridad.clave.label("autoridad_clave"),
            DgtRuta.clave.label("dgt_ruta_clave"),
            DgtEntrega.expediente,
            DgtEntrega.archivo_nombre,
            DgtEntrega.ultimo_evento,
            DgtEntrega.ultimo_evento_creado,
            DgtEntrega.es_anomalo,
        )
        .select_from(DgtEntrega)
        .join(Autoridad, DgtEntrega.autoridad_id == Autoridad.id)
        .join(DgtRuta, DgtEntrega.dgt_ruta_id == DgtRuta.id)
        .where(*where_clauses)
        .order_by(DgtEntrega.ultimo_evento_creado.desc())
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.autoridad_clave,
                item.dgt_ruta_clave,
                item.expediente or "",
                item.archivo_nombre,
                item.ultimo_evento,
                item.ultimo_evento_creado.strftime("%Y-%m-%d %H:%M"),
                "Sí" if item.es_anomalo else "No",
            )
    console.print(tabla)
