"""
Exhortos Archivos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_id, safe_opcion, safe_opcion_int, safe_string
from pjecz_hercules_cli_typer.models.exh_exhortos import ExhExhorto
from pjecz_hercules_cli_typer.models.exh_exhortos_archivos import ExhExhortoArchivo

app = Typer(help="Exhortos Archivos")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    exh_exhorto_id: int | None = None,
    nombre_archivo: str | None = None,
    tipo_documento: int | None = None,
    estado: str | None = None,
):
    """Consultar archivos de exhortos"""
    console = Console()
    console.print("Consultando archivos de exhortos...")

    # Preparar tabla
    tabla = Table(title="Exhortos Archivos")
    tabla.add_column("Exhorto ID", header_style="green", no_wrap=True)
    tabla.add_column("Nombre archivo", header_style="green")
    tabla.add_column("Tipo documento", header_style="green")
    tabla.add_column("Tamaño", header_style="green")
    tabla.add_column("Recepción", header_style="green", no_wrap=True)
    tabla.add_column("Estado", header_style="green")

    # Cláusulas where
    where_clauses = [ExhExhortoArchivo.estatus == "A", ExhExhorto.estatus == "A"]
    if exh_exhorto_id is not None:
        where_clauses.append(ExhExhortoArchivo.exh_exhorto_id == safe_id(exh_exhorto_id))
    if nombre_archivo and (nombre_archivo := safe_string(nombre_archivo)):
        where_clauses.append(ExhExhortoArchivo.nombre_archivo.like("%" + nombre_archivo + "%"))
    if tipo_documento is not None:
        where_clauses.append(
            ExhExhortoArchivo.tipo_documento == safe_opcion_int(tipo_documento, ExhExhortoArchivo.TIPOS_DOCUMENTOS)
        )
    if estado and (estado := safe_opcion(estado, ExhExhortoArchivo.ESTADOS)):
        where_clauses.append(ExhExhortoArchivo.estado == estado)

    # Sentencia
    stmt = (
        select(
            ExhExhortoArchivo.exh_exhorto_id,
            ExhExhortoArchivo.nombre_archivo,
            ExhExhortoArchivo.tipo_documento,
            ExhExhortoArchivo.tamano,
            ExhExhortoArchivo.fecha_hora_recepcion,
            ExhExhortoArchivo.estado,
        )
        .select_from(ExhExhortoArchivo)
        .join(ExhExhorto, ExhExhortoArchivo.exh_exhorto_id == ExhExhorto.id)
        .where(*where_clauses)
        .order_by(ExhExhortoArchivo.fecha_hora_recepcion.desc())
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                str(item.exh_exhorto_id),
                item.nombre_archivo,
                ExhExhortoArchivo.TIPOS_DOCUMENTOS.get(item.tipo_documento, str(item.tipo_documento)),
                str(item.tamano) if item.tamano is not None else "",
                item.fecha_hora_recepcion.strftime("%Y-%m-%d %H:%M"),
                item.estado,
            )
    console.print(tabla)
