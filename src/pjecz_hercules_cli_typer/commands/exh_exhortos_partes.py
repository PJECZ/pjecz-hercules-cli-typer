"""
Exhortos Partes
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_id, safe_opcion_int, safe_string
from pjecz_hercules_cli_typer.models.exh_exhortos import ExhExhorto
from pjecz_hercules_cli_typer.models.exh_exhortos_partes import ExhExhortoParte

app = Typer(help="Exhortos Partes")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    exh_exhorto_id: int | None = None,
    nombre: str | None = None,
    apellido_paterno: str | None = None,
    apellido_materno: str | None = None,
    tipo_parte: int | None = None,
):
    """Consultar partes de exhortos"""
    console = Console()
    console.print("Consultando partes de exhortos...")

    # Preparar tabla
    tabla = Table(title="Exhortos Partes")
    tabla.add_column("Exhorto ID", header_style="green", no_wrap=True)
    tabla.add_column("Nombre", header_style="green")
    tabla.add_column("Apellido paterno", header_style="green")
    tabla.add_column("Apellido materno", header_style="green")
    tabla.add_column("Género", header_style="green")
    tabla.add_column("Persona moral", header_style="green")
    tabla.add_column("Tipo parte", header_style="green")

    # Cláusulas where
    where_clauses = [ExhExhortoParte.estatus == "A", ExhExhorto.estatus == "A"]
    if exh_exhorto_id is not None:
        where_clauses.append(ExhExhortoParte.exh_exhorto_id == safe_id(exh_exhorto_id))
    if nombre and (nombre := safe_string(nombre)):
        where_clauses.append(ExhExhortoParte.nombre.like("%" + nombre + "%"))
    if apellido_paterno and (apellido_paterno := safe_string(apellido_paterno)):
        where_clauses.append(ExhExhortoParte.apellido_paterno.like("%" + apellido_paterno + "%"))
    if apellido_materno and (apellido_materno := safe_string(apellido_materno)):
        where_clauses.append(ExhExhortoParte.apellido_materno.like("%" + apellido_materno + "%"))
    if tipo_parte is not None:
        where_clauses.append(ExhExhortoParte.tipo_parte == safe_opcion_int(tipo_parte, ExhExhortoParte.TIPOS_PARTES))

    # Sentencia
    stmt = (
        select(
            ExhExhortoParte.exh_exhorto_id,
            ExhExhortoParte.nombre,
            ExhExhortoParte.apellido_paterno,
            ExhExhortoParte.apellido_materno,
            ExhExhortoParte.genero,
            ExhExhortoParte.es_persona_moral,
            ExhExhortoParte.tipo_parte,
        )
        .select_from(ExhExhortoParte)
        .join(ExhExhorto, ExhExhortoParte.exh_exhorto_id == ExhExhorto.id)
        .where(*where_clauses)
        .order_by(ExhExhortoParte.exh_exhorto_id, ExhExhortoParte.nombre)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                str(item.exh_exhorto_id),
                item.nombre,
                item.apellido_paterno or "",
                item.apellido_materno or "",
                ExhExhortoParte.GENEROS.get(item.genero, item.genero),
                "Sí" if item.es_persona_moral else "No",
                ExhExhortoParte.TIPOS_PARTES.get(item.tipo_parte, str(item.tipo_parte)),
            )
    console.print(tabla)
