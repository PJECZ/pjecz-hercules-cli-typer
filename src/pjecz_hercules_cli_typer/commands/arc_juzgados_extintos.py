"""
Archivo Juzgados Extintos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_string
from pjecz_hercules_cli_typer.models.arc_juzgados_extintos import ArcJuzgadoExtinto
from pjecz_hercules_cli_typer.models.distritos import Distrito

app = Typer(help="Archivo Juzgados Extintos")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    distrito_clave: str | None = None,
    clave: str | None = None,
    descripcion_corta: str | None = None,
):
    """Consultar juzgados extintos del archivo"""
    console = Console()
    console.print("Consultando juzgados extintos del archivo...")

    # Preparar tabla
    tabla = Table(title="Archivo Juzgados Extintos")
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Descripción corta", header_style="green")
    tabla.add_column("Distrito", header_style="green", no_wrap=True)

    # Cláusulas where
    where_clauses = [ArcJuzgadoExtinto.estatus == "A", Distrito.estatus == "A"]
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        where_clauses.append(Distrito.clave == distrito_clave)
    if clave and (clave := safe_clave(clave)):
        where_clauses.append(ArcJuzgadoExtinto.clave == clave)
    if descripcion_corta and (descripcion_corta := safe_string(descripcion_corta)):
        where_clauses.append(ArcJuzgadoExtinto.descripcion_corta.like("%" + descripcion_corta + "%"))

    # Sentencia
    stmt = (
        select(
            ArcJuzgadoExtinto.clave,
            ArcJuzgadoExtinto.descripcion_corta,
            Distrito.clave.label("distrito_clave"),
        )
        .select_from(ArcJuzgadoExtinto)
        .join(Distrito, ArcJuzgadoExtinto.distrito_id == Distrito.id)
        .where(*where_clauses)
        .order_by(ArcJuzgadoExtinto.clave)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.clave, item.descripcion_corta, item.distrito_clave)
    console.print(tabla)
