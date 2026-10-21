"""
REPSVM Agresores
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_opcion, safe_string
from pjecz_hercules_cli_typer.models.distritos import Distrito
from pjecz_hercules_cli_typer.models.repsvm_agresores import RepsvmAgresor

app = Typer(help="REPSVM Agresores")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    distrito_clave: str | None = None,
    nombre: str | None = None,
    numero_causa: str | None = None,
    delito_generico: str | None = None,
    tipo_juzgado: str | None = None,
    tipo_sentencia: str | None = None,
    es_publico: bool | None = None,
):
    """Consultar agresores del REPSVM"""
    console = Console()
    console.print("Consultando agresores del REPSVM...")

    # Preparar tabla
    tabla = Table(title="REPSVM Agresores")
    tabla.add_column("Distrito", header_style="green", no_wrap=True)
    tabla.add_column("Consecutivo", header_style="green")
    tabla.add_column("Nombre", header_style="green")
    tabla.add_column("Número causa", header_style="green", no_wrap=True)
    tabla.add_column("Delito genérico", header_style="green")
    tabla.add_column("Tipo juzgado", header_style="green")
    tabla.add_column("Tipo sentencia", header_style="green")
    tabla.add_column("Público", header_style="green")

    # Cláusulas where
    where_clauses = [RepsvmAgresor.estatus == "A", Distrito.estatus == "A"]
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        where_clauses.append(Distrito.clave == distrito_clave)
    if nombre and (nombre := safe_string(nombre)):
        where_clauses.append(RepsvmAgresor.nombre.like("%" + nombre + "%"))
    if numero_causa and (numero_causa := safe_string(numero_causa)):
        where_clauses.append(RepsvmAgresor.numero_causa.like("%" + numero_causa + "%"))
    if delito_generico and (delito_generico := safe_string(delito_generico)):
        where_clauses.append(RepsvmAgresor.delito_generico.like("%" + delito_generico + "%"))
    if tipo_juzgado and (tipo_juzgado := safe_opcion(tipo_juzgado, RepsvmAgresor.TIPOS_JUZGADOS)):
        where_clauses.append(RepsvmAgresor.tipo_juzgado == tipo_juzgado)
    if tipo_sentencia and (tipo_sentencia := safe_opcion(tipo_sentencia, RepsvmAgresor.TIPOS_SENTENCIAS)):
        where_clauses.append(RepsvmAgresor.tipo_sentencia == tipo_sentencia)
    if es_publico is not None:
        where_clauses.append(RepsvmAgresor.es_publico == es_publico)

    # Sentencia
    stmt = (
        select(
            Distrito.clave.label("distrito_clave"),
            RepsvmAgresor.consecutivo,
            RepsvmAgresor.nombre,
            RepsvmAgresor.numero_causa,
            RepsvmAgresor.delito_generico,
            RepsvmAgresor.tipo_juzgado,
            RepsvmAgresor.tipo_sentencia,
            RepsvmAgresor.es_publico,
        )
        .select_from(RepsvmAgresor)
        .join(Distrito, RepsvmAgresor.distrito_id == Distrito.id)
        .where(*where_clauses)
        .order_by(Distrito.clave, RepsvmAgresor.consecutivo)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.distrito_clave,
                str(item.consecutivo),
                item.nombre,
                item.numero_causa,
                item.delito_generico,
                item.tipo_juzgado,
                item.tipo_sentencia,
                "Sí" if item.es_publico else "No",
            )
    console.print(tabla)
