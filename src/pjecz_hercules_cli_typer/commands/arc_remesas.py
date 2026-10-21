"""
Archivo Remesas
"""

from datetime import timedelta

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_email, safe_fecha, safe_opcion, safe_string
from pjecz_hercules_cli_typer.models.arc_documentos_tipos import ArcDocumentoTipo
from pjecz_hercules_cli_typer.models.arc_remesas import ArcRemesa
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.usuarios import Usuario

app = Typer(help="Archivo Remesas")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    autoridad_clave: str | None = None,
    usuario_asignado_email: str | None = None,
    arc_documento_tipo_nombre: str | None = None,
    num_oficio: str | None = None,
    anio: str | None = None,
    estado: str | None = None,
    tiempo_enviado_desde: str | None = None,
    tiempo_enviado_hasta: str | None = None,
):
    """Consultar remesas del archivo"""
    console = Console()
    console.print("Consultando remesas del archivo...")

    # Preparar tabla
    tabla = Table(title="Archivo Remesas")
    tabla.add_column("ID", header_style="green", no_wrap=True)
    tabla.add_column("Autoridad", header_style="green", no_wrap=True)
    tabla.add_column("Oficio", header_style="green", no_wrap=True)
    tabla.add_column("Año", header_style="green")
    tabla.add_column("Tipo", header_style="green")
    tabla.add_column("Asignado", header_style="green", no_wrap=True)
    tabla.add_column("Enviado", header_style="green", no_wrap=True)
    tabla.add_column("Documentos", header_style="green")
    tabla.add_column("Anomalías", header_style="green")
    tabla.add_column("Estado", header_style="green")

    # Cláusulas where
    where_clauses = [ArcRemesa.estatus == "A", Autoridad.estatus == "A", ArcDocumentoTipo.estatus == "A"]
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        where_clauses.append(Autoridad.clave == autoridad_clave)
    if usuario_asignado_email and (usuario_asignado_email := safe_email(usuario_asignado_email)):
        where_clauses.append(Usuario.estatus == "A")
        where_clauses.append(Usuario.email == usuario_asignado_email)
    if arc_documento_tipo_nombre and (arc_documento_tipo_nombre := safe_string(arc_documento_tipo_nombre)):
        where_clauses.append(ArcDocumentoTipo.nombre == arc_documento_tipo_nombre)
    if num_oficio and (num_oficio := safe_string(num_oficio)):
        where_clauses.append(ArcRemesa.num_oficio.like("%" + num_oficio + "%"))
    if anio and (anio := safe_string(anio)):
        where_clauses.append(ArcRemesa.anio == anio)
    if estado and (estado := safe_opcion(estado, ArcRemesa.ESTADOS)):
        where_clauses.append(ArcRemesa.estado == estado)
    if tiempo_enviado_desde and (desde := safe_fecha(tiempo_enviado_desde)):
        where_clauses.append(ArcRemesa.tiempo_enviado >= desde)
    if tiempo_enviado_hasta and (hasta := safe_fecha(tiempo_enviado_hasta)):
        where_clauses.append(ArcRemesa.tiempo_enviado < hasta + timedelta(days=1))

    # Sentencia
    stmt = (
        select(
            ArcRemesa.id,
            Autoridad.clave.label("autoridad_clave"),
            ArcRemesa.num_oficio,
            ArcRemesa.anio,
            ArcDocumentoTipo.nombre.label("arc_documento_tipo_nombre"),
            Usuario.email.label("usuario_asignado_email"),
            ArcRemesa.tiempo_enviado,
            ArcRemesa.num_documentos,
            ArcRemesa.num_anomalias,
            ArcRemesa.estado,
        )
        .select_from(ArcRemesa)
        .join(Autoridad, ArcRemesa.autoridad_id == Autoridad.id)
        .join(ArcDocumentoTipo, ArcRemesa.arc_documento_tipo_id == ArcDocumentoTipo.id)
        .outerjoin(Usuario, ArcRemesa.usuario_asignado_id == Usuario.id)
        .where(*where_clauses)
        .order_by(ArcRemesa.tiempo_enviado.desc())
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                str(item.id),
                item.autoridad_clave,
                item.num_oficio,
                item.anio or "",
                item.arc_documento_tipo_nombre,
                item.usuario_asignado_email or "",
                item.tiempo_enviado.strftime("%Y-%m-%d %H:%M") if item.tiempo_enviado else "",
                str(item.num_documentos),
                str(item.num_anomalias),
                item.estado,
            )
    console.print(tabla)
