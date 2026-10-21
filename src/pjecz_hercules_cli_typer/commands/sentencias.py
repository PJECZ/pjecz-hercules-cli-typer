"""
Sentencias
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_fecha, safe_string
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.materias_tipos_juicios import MateriaTipoJuicio
from pjecz_hercules_cli_typer.models.sentencias import Sentencia

app = Typer(help="Sentencias")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    autoridad_clave: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    sentencia: str | None = None,
    expediente: str | None = None,
    descripcion: str | None = None,
    es_perspectiva_genero: bool | None = None,
):
    """Consultar sentencias"""
    console = Console()
    console.print("Consultando sentencias...")

    # Preparar tabla
    tabla = Table(title="Sentencias")
    tabla.add_column("Fecha", header_style="green", no_wrap=True)
    tabla.add_column("Autoridad", header_style="green", no_wrap=True)
    tabla.add_column("Sentencia", header_style="green", no_wrap=True)
    tabla.add_column("Expediente", header_style="green", no_wrap=True)
    tabla.add_column("Tipo de juicio", header_style="green")
    tabla.add_column("Descripción", header_style="green")
    tabla.add_column("P. género", header_style="green")

    # Cláusulas where
    where_clauses = [Sentencia.estatus == "A", Autoridad.estatus == "A", MateriaTipoJuicio.estatus == "A"]
    autoridad_clave = safe_clave(autoridad_clave)
    if autoridad_clave:
        where_clauses.append(Autoridad.clave == autoridad_clave)
    if fecha_desde:
        where_clauses.append(Sentencia.fecha >= safe_fecha(fecha_desde))
    if fecha_hasta:
        where_clauses.append(Sentencia.fecha <= safe_fecha(fecha_hasta))
    sentencia = safe_string(sentencia)
    if sentencia:
        where_clauses.append(Sentencia.sentencia.like("%" + sentencia + "%"))
    expediente = safe_string(expediente)
    if expediente:
        where_clauses.append(Sentencia.expediente.like("%" + expediente + "%"))
    descripcion = safe_string(descripcion, save_enie=True)
    if descripcion:
        where_clauses.append(Sentencia.descripcion.like("%" + descripcion + "%"))
    if es_perspectiva_genero is not None:
        where_clauses.append(Sentencia.es_perspectiva_genero == es_perspectiva_genero)

    # Sentencia
    stmt = (
        select(
            Sentencia.fecha,
            Autoridad.clave.label("autoridad_clave"),
            Sentencia.sentencia,
            Sentencia.expediente,
            MateriaTipoJuicio.descripcion.label("materia_tipo_juicio_descripcion"),
            Sentencia.descripcion,
            Sentencia.es_perspectiva_genero,
        )
        .select_from(Sentencia)
        .join(Autoridad, Sentencia.autoridad_id == Autoridad.id)
        .join(MateriaTipoJuicio, Sentencia.materia_tipo_juicio_id == MateriaTipoJuicio.id)
        .where(*where_clauses)
        .order_by(Sentencia.fecha.desc(), Autoridad.clave)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.fecha.strftime("%Y-%m-%d"),
                item.autoridad_clave,
                item.sentencia,
                item.expediente,
                item.materia_tipo_juicio_descripcion,
                item.descripcion,
                "Sí" if item.es_perspectiva_genero else "No",
            )
    console.print(tabla)
