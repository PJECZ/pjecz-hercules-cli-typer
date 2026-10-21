"""
Archivo Remesas Documentos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_id, safe_opcion
from pjecz_hercules_cli_typer.models.arc_documentos import ArcDocumento
from pjecz_hercules_cli_typer.models.arc_remesas import ArcRemesa
from pjecz_hercules_cli_typer.models.arc_remesas_documentos import ArcRemesaDocumento

app = Typer(help="Archivo Remesas Documentos")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    arc_remesa_id: int | None = None,
    arc_documento_id: int | None = None,
    tipo_juzgado: str | None = None,
    anomalia: str | None = None,
):
    """Consultar documentos de las remesas del archivo"""
    console = Console()
    console.print("Consultando documentos de las remesas del archivo...")

    # Preparar tabla
    tabla = Table(title="Archivo Remesas Documentos")
    tabla.add_column("Remesa ID", header_style="green", no_wrap=True)
    tabla.add_column("Documento ID", header_style="green", no_wrap=True)
    tabla.add_column("Expediente", header_style="green", no_wrap=True)
    tabla.add_column("Tipo juzgado", header_style="green")
    tabla.add_column("Fojas", header_style="green")
    tabla.add_column("Anomalía", header_style="green")

    # Cláusulas where
    where_clauses = [ArcRemesaDocumento.estatus == "A", ArcRemesa.estatus == "A", ArcDocumento.estatus == "A"]
    if arc_remesa_id is not None:
        where_clauses.append(ArcRemesaDocumento.arc_remesa_id == safe_id(arc_remesa_id))
    if arc_documento_id is not None:
        where_clauses.append(ArcRemesaDocumento.arc_documento_id == safe_id(arc_documento_id))
    if tipo_juzgado and (tipo_juzgado := safe_opcion(tipo_juzgado, ArcRemesaDocumento.TIPOS)):
        where_clauses.append(ArcRemesaDocumento.tipo_juzgado == tipo_juzgado)
    if anomalia and (anomalia := safe_opcion(anomalia, ArcRemesaDocumento.ANOMALIAS)):
        where_clauses.append(ArcRemesaDocumento.anomalia == anomalia)

    # Sentencia
    stmt = (
        select(
            ArcRemesaDocumento.arc_remesa_id,
            ArcRemesaDocumento.arc_documento_id,
            ArcDocumento.expediente,
            ArcRemesaDocumento.tipo_juzgado,
            ArcRemesaDocumento.fojas,
            ArcRemesaDocumento.anomalia,
        )
        .select_from(ArcRemesaDocumento)
        .join(ArcRemesa, ArcRemesaDocumento.arc_remesa_id == ArcRemesa.id)
        .join(ArcDocumento, ArcRemesaDocumento.arc_documento_id == ArcDocumento.id)
        .where(*where_clauses)
        .order_by(ArcDocumento.expediente)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                str(item.arc_remesa_id),
                str(item.arc_documento_id),
                item.expediente,
                item.tipo_juzgado,
                str(item.fojas),
                item.anomalia or "",
            )
    console.print(tabla)
