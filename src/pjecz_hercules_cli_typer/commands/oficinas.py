"""
Oficinas
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_string
from pjecz_hercules_cli_typer.models.distritos import Distrito
from pjecz_hercules_cli_typer.models.domicilios import Domicilio
from pjecz_hercules_cli_typer.models.oficinas import Oficina

app = Typer(help="Oficinas")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    distrito_clave: str | None = None,
    domicilio_edificio: str | None = None,
    clave: str | None = None,
    descripcion: str | None = None,
    descripcion_corta: str | None = None,
    es_jurisdiccional: bool | None = None,
):
    """Consultar oficinas"""
    console = Console()
    console.print("Consultando oficinas...")

    # Preparar tabla
    tabla = Table(title="Oficinas")
    tabla.add_column("Clave", header_style="green", no_wrap=True)
    tabla.add_column("Descripción corta", header_style="green")
    tabla.add_column("Distrito", header_style="green", no_wrap=True)
    tabla.add_column("Edificio", header_style="green")
    tabla.add_column("Jurisdiccional", header_style="green")

    # Cláusulas where
    where_clauses = [Oficina.estatus == "A", Distrito.estatus == "A", Domicilio.estatus == "A"]
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        where_clauses.append(Distrito.clave == distrito_clave)
    if domicilio_edificio and (domicilio_edificio := safe_string(domicilio_edificio)):
        where_clauses.append(Domicilio.edificio == domicilio_edificio)
    if clave and (clave := safe_clave(clave, max_len=32)):
        where_clauses.append(Oficina.clave == clave)
    if descripcion and (descripcion := safe_string(descripcion)):
        where_clauses.append(Oficina.descripcion.like("%" + descripcion + "%"))
    if descripcion_corta and (descripcion_corta := safe_string(descripcion_corta)):
        where_clauses.append(Oficina.descripcion_corta.like("%" + descripcion_corta + "%"))
    if es_jurisdiccional is not None:
        where_clauses.append(Oficina.es_jurisdiccional == es_jurisdiccional)

    # Sentencia
    stmt = (
        select(
            Oficina.clave,
            Oficina.descripcion_corta,
            Distrito.clave.label("distrito_clave"),
            Domicilio.edificio.label("domicilio_edificio"),
            Oficina.es_jurisdiccional,
        )
        .select_from(Oficina)
        .join(Distrito, Oficina.distrito_id == Distrito.id)
        .join(Domicilio, Oficina.domicilio_id == Domicilio.id)
        .where(*where_clauses)
        .order_by(Oficina.clave)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.clave,
                item.descripcion_corta,
                item.distrito_clave,
                item.domicilio_edificio,
                "Sí" if item.es_jurisdiccional else "No",
            )
    console.print(tabla)
