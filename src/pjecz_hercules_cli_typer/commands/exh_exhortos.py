"""
Exhortos
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import func, select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_opcion, safe_string
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.exh_areas import ExhArea
from pjecz_hercules_cli_typer.models.exh_exhortos import ExhExhorto
from pjecz_hercules_cli_typer.models.exh_tipos_diligencias import ExhTipoDiligencia

app = Typer(help="Exhortos")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    autoridad_clave: str | None = None,
    exh_area_clave: str | None = None,
    exh_tipo_diligencia_clave: str | None = None,
    exhorto_origen_id: str | None = None,
    numero_expediente_origen: str | None = None,
    juzgado_origen_nombre: str | None = None,
    materia_clave: str | None = None,
    remitente: str | None = None,
    estado: str | None = None,
):
    """Consultar exhortos"""
    console = Console()
    console.print("Consultando exhortos...")

    # Preparar tabla
    tabla = Table(title="Exhortos")
    tabla.add_column("ID", header_style="green", no_wrap=True)
    tabla.add_column("Autoridad", header_style="green", no_wrap=True)
    tabla.add_column("Área", header_style="green", no_wrap=True)
    tabla.add_column("Tipo diligencia", header_style="green", no_wrap=True)
    tabla.add_column("Exhorto origen ID", header_style="green", no_wrap=True)
    tabla.add_column("Expediente origen", header_style="green")
    tabla.add_column("Juzgado origen", header_style="green")
    tabla.add_column("Materia", header_style="green")
    tabla.add_column("Remitente", header_style="green")
    tabla.add_column("Estado", header_style="green")

    # Cláusulas where
    where_clauses = [
        ExhExhorto.estatus == "A",
        Autoridad.estatus == "A",
        ExhArea.estatus == "A",
        ExhTipoDiligencia.estatus == "A",
    ]
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        where_clauses.append(Autoridad.clave == autoridad_clave)
    if exh_area_clave and (exh_area_clave := safe_clave(exh_area_clave)):
        where_clauses.append(ExhArea.clave == exh_area_clave)
    if exh_tipo_diligencia_clave and (exh_tipo_diligencia_clave := safe_clave(exh_tipo_diligencia_clave)):
        where_clauses.append(ExhTipoDiligencia.clave == exh_tipo_diligencia_clave)
    if exhorto_origen_id and (exhorto_origen_id := safe_string(exhorto_origen_id, max_len=64)):
        where_clauses.append(func.upper(ExhExhorto.exhorto_origen_id) == exhorto_origen_id)
    if numero_expediente_origen and (numero_expediente_origen := safe_string(numero_expediente_origen)):
        where_clauses.append(ExhExhorto.numero_expediente_origen.like("%" + numero_expediente_origen + "%"))
    if juzgado_origen_nombre and (juzgado_origen_nombre := safe_string(juzgado_origen_nombre)):
        where_clauses.append(ExhExhorto.juzgado_origen_nombre.like("%" + juzgado_origen_nombre + "%"))
    if materia_clave and (materia_clave := safe_clave(materia_clave, max_len=32)):
        where_clauses.append(ExhExhorto.materia_clave == materia_clave)
    if remitente and (remitente := safe_opcion(remitente, ExhExhorto.REMITENTES)):
        where_clauses.append(ExhExhorto.remitente == remitente)
    if estado and (estado := safe_opcion(estado, ExhExhorto.ESTADOS)):
        where_clauses.append(ExhExhorto.estado == estado)

    # Sentencia
    stmt = (
        select(
            ExhExhorto.id,
            Autoridad.clave.label("autoridad_clave"),
            ExhArea.clave.label("exh_area_clave"),
            ExhTipoDiligencia.clave.label("exh_tipo_diligencia_clave"),
            ExhExhorto.exhorto_origen_id,
            ExhExhorto.numero_expediente_origen,
            ExhExhorto.juzgado_origen_nombre,
            ExhExhorto.materia_nombre,
            ExhExhorto.remitente,
            ExhExhorto.estado,
        )
        .select_from(ExhExhorto)
        .join(Autoridad, ExhExhorto.autoridad_id == Autoridad.id)
        .join(ExhArea, ExhExhorto.exh_area_id == ExhArea.id)
        .join(ExhTipoDiligencia, ExhExhorto.exh_tipo_diligencia_id == ExhTipoDiligencia.id)
        .where(*where_clauses)
        .order_by(ExhExhorto.id.desc())
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                str(item.id),
                item.autoridad_clave,
                item.exh_area_clave,
                item.exh_tipo_diligencia_clave,
                item.exhorto_origen_id,
                item.numero_expediente_origen,
                item.juzgado_origen_nombre,
                item.materia_nombre,
                item.remitente,
                item.estado,
            )
    console.print(tabla)
