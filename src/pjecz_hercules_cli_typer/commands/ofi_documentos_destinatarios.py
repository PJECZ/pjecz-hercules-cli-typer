"""
Oficios Documentos Destinatarios
"""

import uuid

from rich.console import Console
from rich.table import Table
from sqlalchemy import func, insert, select, update
from typer import Exit, Typer, confirm

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.ofi_documentos import OfiDocumento
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


@app.command()
def agregar_todos(ofi_documento_id: uuid.UUID):
    """Agregar como destinatarios a todos los usuarios activos con CURP"""
    console = Console()

    with session_scope() as session:
        # Validar que exista el oficio documento
        if session.get(OfiDocumento, ofi_documento_id) is None:
            console.print(f"[red]No existe el oficio documento {ofi_documento_id}[/red]")
            raise Exit(1)

        # Consultar los usuarios activos con CURP
        stmt = select(Usuario.id).where(Usuario.estatus == "A", Usuario.curp.is_not(None), func.trim(Usuario.curp) != "")
        usuarios_ids = session.execute(stmt).scalars().all()

        # Consultar los destinatarios que ya tiene el oficio documento, sin importar su estatus
        stmt = select(
            OfiDocumentoDestinatario.id,
            OfiDocumentoDestinatario.usuario_id,
            OfiDocumentoDestinatario.estatus,
        ).where(OfiDocumentoDestinatario.ofi_documento_id == ofi_documento_id)
        usuarios_activos = set()
        destinatarios_eliminados = {}
        for item in session.execute(stmt).all():
            if item.estatus == "A":
                usuarios_activos.add(item.usuario_id)
            else:
                destinatarios_eliminados[item.usuario_id] = item.id

        # Separar los usuarios a insertar y los destinatarios a recuperar; se omiten los que ya están activos
        insertar = []
        recuperar = []
        for usuario_id in usuarios_ids:
            if usuario_id in usuarios_activos:
                continue
            if usuario_id in destinatarios_eliminados:
                recuperar.append(destinatarios_eliminados[usuario_id])
            else:
                insertar.append(usuario_id)

        # Confirmar antes de agregar
        if insertar or recuperar:
            confirm(
                f"¿Insertar {len(insertar)} y recuperar {len(recuperar)} destinatarios "
                f"del oficio documento {ofi_documento_id}?",
                abort=True,
            )

        # Insertar los nuevos destinatarios
        if insertar:
            session.execute(
                insert(OfiDocumentoDestinatario),
                [{"ofi_documento_id": ofi_documento_id, "usuario_id": usuario_id} for usuario_id in insertar],
            )

        # Cambiar el estatus a A de los destinatarios eliminados
        if recuperar:
            session.execute(
                update(OfiDocumentoDestinatario).where(OfiDocumentoDestinatario.id.in_(recuperar)).values(estatus="A")
            )

        # Contar los destinatarios activos
        stmt = (
            select(func.count())
            .select_from(OfiDocumentoDestinatario)
            .where(
                OfiDocumentoDestinatario.estatus == "A",
                OfiDocumentoDestinatario.ofi_documento_id == ofi_documento_id,
            )
        )
        cantidad = session.execute(stmt).scalar_one()

    console.print(f"Se insertaron {len(insertar)} y se recuperaron {len(recuperar)} destinatarios.")
    console.print(f"El oficio documento tiene {cantidad} destinatarios activos.")
