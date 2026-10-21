"""
Glosas
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_string, safe_tipo_juicio
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.glosas import Glosa

app = Typer(help="Glosas")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    autoridad_clave: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    tipo_juicio: str | None = None,
    expediente: str | None = None,
    descripcion: str | None = None,
):
    """Consultar glosas"""
    console = Console()
    console.print("Consultando glosas...")

    # Preparar tabla
    tabla = Table(title="Glosas")
    tabla.add_column("Fecha", header_style="green", no_wrap=True)
    tabla.add_column("Autoridad", header_style="green", no_wrap=True)
    tabla.add_column("Tipo de juicio", header_style="green")
    tabla.add_column("Expediente", header_style="green", no_wrap=True)
    tabla.add_column("Descripción", header_style="green")

    # Cláusulas where
    where_clauses = [Glosa.estatus == "A", Autoridad.estatus == "A"]
    autoridad_clave = safe_clave(autoridad_clave)
    if autoridad_clave:
        where_clauses.append(Autoridad.clave == autoridad_clave)
    if fecha_desde:
        where_clauses.append(Glosa.fecha >= safe_fecha(fecha_desde))
    if fecha_hasta:
        where_clauses.append(Glosa.fecha <= safe_fecha(fecha_hasta))
    tipo_juicio = safe_string(tipo_juicio)
    if tipo_juicio:
        safe_tipo_juicio(tipo_juicio, Glosa.TIPOS_JUICIOS)
        where_clauses.append(Glosa.tipo_juicio == tipo_juicio)
    expediente = safe_string(expediente)
    if expediente:
        where_clauses.append(Glosa.expediente.like("%" + expediente + "%"))
    descripcion = safe_string(descripcion, save_enie=True)
    if descripcion:
        where_clauses.append(Glosa.descripcion.like("%" + descripcion + "%"))

    # Sentencia
    stmt = (
        select(
            Glosa.fecha,
            Autoridad.clave.label("autoridad_clave"),
            Glosa.tipo_juicio,
            Glosa.expediente,
            Glosa.descripcion,
        )
        .select_from(Glosa)
        .join(Autoridad, Glosa.autoridad_id == Autoridad.id)
        .where(*where_clauses)
        .order_by(Glosa.fecha.desc(), Autoridad.clave)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.fecha.strftime("%Y-%m-%d"),
                item.autoridad_clave,
                item.tipo_juicio,
                item.expediente,
                item.descripcion,
            )
    console.print(tabla)
