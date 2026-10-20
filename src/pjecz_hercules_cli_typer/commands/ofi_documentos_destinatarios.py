"""
Oficios Documentos Destinatarios
"""

import uuid

from rich.console import Console
from rich.table import Table
from sqlalchemy import func, select, update
from typer import Typer, confirm

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.ofi_documentos_destinatarios import OfiDocumentoDestinatario
from pjecz_hercules_cli_typer.models.usuarios import Usuario

app = Typer(help="Oficios Documentos Destinatarios")


@app.command()
def consultar(
    ofi_documento_id: uuid.UUID,
    offset: int = 0,
    limit: int = 25,
):
    """Consultar destinatarios de un oficio documento"""
    console = Console()
    console.print("Consultando destinatarios del oficio documento...")

    # Preparar tabla
    tabla = Table(title="Oficios Documentos Destinatarios")
    tabla.add_column("Email", header_style="green", no_wrap=True)
    tabla.add_column("Nombres", header_style="green")
    tabla.add_column("A. Paterno", header_style="green")
    tabla.add_column("A. Materno", header_style="green")
    tabla.add_column("Puesto", header_style="green")
    tabla.add_column("Autoridad", header_style="green", no_wrap=True)
    tabla.add_column("Con copia", header_style="green")
    tabla.add_column("Leído", header_style="green")

    # Cláusulas where
    where_clauses = [
        OfiDocumentoDestinatario.estatus == "A",
        Usuario.estatus == "A",
        Autoridad.estatus == "A",
        OfiDocumentoDestinatario.ofi_documento_id == ofi_documento_id,
    ]

    # Sentencia
    stmt = (
        select(
            Usuario.email.label("usuario_email"),
            Usuario.nombres.label("usuario_nombres"),
            Usuario.apellido_paterno.label("usuario_apellido_paterno"),
            Usuario.apellido_materno.label("usuario_apellido_materno"),
            Usuario.puesto.label("usuario_puesto"),
            Autoridad.clave.label("autoridad_clave"),
            OfiDocumentoDestinatario.con_copia,
            OfiDocumentoDestinatario.fue_leido,
        )
        .select_from(OfiDocumentoDestinatario)
        .join(Usuario, OfiDocumentoDestinatario.usuario_id == Usuario.id)
        .join(Autoridad, Usuario.autoridad_id == Autoridad.id)
        .where(*where_clauses)
        .order_by(OfiDocumentoDestinatario.con_copia, Usuario.email)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.usuario_email,
                item.usuario_nombres,
                item.usuario_apellido_paterno,
                item.usuario_apellido_materno,
                item.usuario_puesto or "",
                item.autoridad_clave,
                "Sí" if item.con_copia else "No",
                "Sí" if item.fue_leido else "No",
            )
    console.print(tabla)


@app.command()
def eliminar_todos(ofi_documento_id: uuid.UUID):
    """Eliminar todos los destinatarios de un oficio documento (cambia su estatus a B)"""
    console = Console()

    # Cláusulas where
    where_clauses = [
        OfiDocumentoDestinatario.estatus == "A",
        OfiDocumentoDestinatario.ofi_documento_id == ofi_documento_id,
    ]

    with session_scope() as session:
        # Contar los destinatarios activos
        stmt = select(func.count()).select_from(OfiDocumentoDestinatario).where(*where_clauses)
        cantidad = session.execute(stmt).scalar_one()
        if cantidad == 0:
            console.print("No hay destinatarios activos para ese oficio documento.")
            return

        # Confirmar antes de eliminar
        confirm(f"¿Eliminar {cantidad} destinatarios del oficio documento {ofi_documento_id}?", abort=True)

        # Cambiar el estatus a B
        session.execute(update(OfiDocumentoDestinatario).where(*where_clauses).values(estatus="B"))

    console.print(f"Se eliminaron {cantidad} destinatarios.")
