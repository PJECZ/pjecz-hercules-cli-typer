"""
Archivo Documentos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_expediente, safe_opcion, safe_string
from pjecz_hercules_cli_typer.models.arc_documentos import ArcDocumento
from pjecz_hercules_cli_typer.models.arc_documentos_tipos import ArcDocumentoTipo
from pjecz_hercules_cli_typer.models.arc_juzgados_extintos import ArcJuzgadoExtinto
from pjecz_hercules_cli_typer.models.autoridades import Autoridad

app = Typer(help="Archivo Documentos")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    autoridad_clave: str | None = None,
    arc_juzgado_origen_clave: str | None = None,
    arc_documento_tipo_nombre: str | None = None,
    expediente: str | None = None,
    expediente_numero: int | None = None,
    anio: int | None = None,
    actor: str | None = None,
    demandado: str | None = None,
    tipo_juzgado: str | None = None,
    ubicacion: str | None = None,
):
    """Consultar documentos del archivo"""
    console = Console()
    console.print("Consultando documentos del archivo...")

    # Preparar tabla
    tabla = Table(title="Archivo Documentos")
    tabla.add_column("ID", header_style="green", no_wrap=True)
    tabla.add_column("Autoridad", header_style="green", no_wrap=True)
    tabla.add_column("Expediente", header_style="green", no_wrap=True)
    tabla.add_column("Año", header_style="green")
    tabla.add_column("Actor", header_style="green")
    tabla.add_column("Demandado", header_style="green")
    tabla.add_column("Tipo", header_style="green")
    tabla.add_column("Juzgado origen", header_style="green", no_wrap=True)
    tabla.add_column("Tipo juzgado", header_style="green")
    tabla.add_column("Ubicación", header_style="green")
    tabla.add_column("Fojas", header_style="green")

    # Cláusulas where
    where_clauses = [
        ArcDocumento.estatus == "A",
        Autoridad.estatus == "A",
        ArcJuzgadoExtinto.estatus == "A",
        ArcDocumentoTipo.estatus == "A",
    ]
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        where_clauses.append(Autoridad.clave == autoridad_clave)
    if arc_juzgado_origen_clave and (arc_juzgado_origen_clave := safe_clave(arc_juzgado_origen_clave)):
        where_clauses.append(ArcJuzgadoExtinto.clave == arc_juzgado_origen_clave)
    if arc_documento_tipo_nombre and (arc_documento_tipo_nombre := safe_string(arc_documento_tipo_nombre)):
        where_clauses.append(ArcDocumentoTipo.nombre == arc_documento_tipo_nombre)
    if expediente and (expediente := safe_expediente(expediente)):
        where_clauses.append(ArcDocumento.expediente == expediente)
    if expediente_numero is not None:
        where_clauses.append(ArcDocumento.expediente_numero == expediente_numero)
    if anio is not None:
        where_clauses.append(ArcDocumento.anio == anio)
    if actor and (actor := safe_string(actor)):
        where_clauses.append(ArcDocumento.actor.like("%" + actor + "%"))
    if demandado and (demandado := safe_string(demandado)):
        where_clauses.append(ArcDocumento.demandado.like("%" + demandado + "%"))
    if tipo_juzgado and (tipo_juzgado := safe_opcion(tipo_juzgado, ArcDocumento.TIPO_JUZGADOS)):
        where_clauses.append(ArcDocumento.tipo_juzgado == tipo_juzgado)
    if ubicacion and (ubicacion := safe_opcion(ubicacion, ArcDocumento.UBICACIONES)):
        where_clauses.append(ArcDocumento.ubicacion == ubicacion)

    # Sentencia
    stmt = (
        select(
            ArcDocumento.id,
            Autoridad.clave.label("autoridad_clave"),
            ArcDocumento.expediente,
            ArcDocumento.anio,
            ArcDocumento.actor,
            ArcDocumento.demandado,
            ArcDocumentoTipo.nombre.label("arc_documento_tipo_nombre"),
            ArcJuzgadoExtinto.clave.label("arc_juzgado_origen_clave"),
            ArcDocumento.tipo_juzgado,
            ArcDocumento.ubicacion,
            ArcDocumento.fojas,
        )
        .select_from(ArcDocumento)
        .join(Autoridad, ArcDocumento.autoridad_id == Autoridad.id)
        .join(ArcJuzgadoExtinto, ArcDocumento.arc_juzgado_origen_id == ArcJuzgadoExtinto.id)
        .join(ArcDocumentoTipo, ArcDocumento.arc_documento_tipo_id == ArcDocumentoTipo.id)
        .where(*where_clauses)
        .order_by(ArcDocumento.expediente)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                str(item.id),
                item.autoridad_clave,
                item.expediente,
                str(item.anio),
                item.actor,
                item.demandado or "",
                item.arc_documento_tipo_nombre,
                item.arc_juzgado_origen_clave,
                item.tipo_juzgado,
                item.ubicacion,
                str(item.fojas),
            )
    console.print(tabla)
