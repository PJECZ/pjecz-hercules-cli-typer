"""
Soportes Tickets
"""

from datetime import timedelta

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_curp, safe_email, safe_fecha, safe_opcion, safe_string
from pjecz_hercules_cli_typer.models.funcionarios import Funcionario
from pjecz_hercules_cli_typer.models.soportes_categorias import SoporteCategoria
from pjecz_hercules_cli_typer.models.soportes_tickets import SoporteTicket
from pjecz_hercules_cli_typer.models.usuarios import Usuario

app = Typer(help="Soportes Tickets")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    usuario_email: str | None = None,
    funcionario_curp: str | None = None,
    funcionario_email: str | None = None,
    soporte_categoria_nombre: str | None = None,
    departamento: str | None = None,
    estado: str | None = None,
    descripcion: str | None = None,
    creado_desde: str | None = None,
    creado_hasta: str | None = None,
):
    """Consultar tickets de soportes"""
    console = Console()
    console.print("Consultando tickets de soportes...")

    # Preparar tabla
    tabla = Table(title="Soportes Tickets")
    tabla.add_column("ID", header_style="green", no_wrap=True)
    tabla.add_column("Creado", header_style="green", no_wrap=True)
    tabla.add_column("Usuario", header_style="green", no_wrap=True)
    tabla.add_column("Categoría", header_style="green")
    tabla.add_column("Funcionario", header_style="green", no_wrap=True)
    tabla.add_column("Departamento", header_style="green")
    tabla.add_column("Estado", header_style="green")
    tabla.add_column("Descripción", header_style="green")

    # Cláusulas where
    where_clauses = [
        SoporteTicket.estatus == "A",
        Funcionario.estatus == "A",
        SoporteCategoria.estatus == "A",
        Usuario.estatus == "A",
    ]
    if usuario_email and (usuario_email := safe_email(usuario_email)):
        where_clauses.append(Usuario.email == usuario_email)
    if funcionario_curp and (funcionario_curp := safe_curp(funcionario_curp)):
        where_clauses.append(Funcionario.curp == funcionario_curp)
    if funcionario_email and (funcionario_email := safe_email(funcionario_email)):
        where_clauses.append(Funcionario.email == funcionario_email)
    if soporte_categoria_nombre and (soporte_categoria_nombre := safe_string(soporte_categoria_nombre)):
        where_clauses.append(SoporteCategoria.nombre == soporte_categoria_nombre)
    if departamento and (departamento := safe_opcion(departamento, SoporteTicket.DEPARTAMENTOS)):
        where_clauses.append(SoporteTicket.departamento == departamento)
    if estado and (estado := safe_opcion(estado, SoporteTicket.ESTADOS)):
        where_clauses.append(SoporteTicket.estado == estado)
    if descripcion and (descripcion := safe_string(descripcion)):
        where_clauses.append(SoporteTicket.descripcion.like("%" + descripcion + "%"))
    if creado_desde and (desde := safe_fecha(creado_desde)):
        where_clauses.append(SoporteTicket.creado >= desde)
    if creado_hasta and (hasta := safe_fecha(creado_hasta)):
        where_clauses.append(SoporteTicket.creado < hasta + timedelta(days=1))

    # Sentencia
    stmt = (
        select(
            SoporteTicket.id,
            SoporteTicket.creado,
            Usuario.email.label("usuario_email"),
            SoporteCategoria.nombre.label("soporte_categoria_nombre"),
            Funcionario.email.label("funcionario_email"),
            SoporteTicket.departamento,
            SoporteTicket.estado,
            SoporteTicket.descripcion,
        )
        .select_from(SoporteTicket)
        .join(Funcionario, SoporteTicket.funcionario_id == Funcionario.id)
        .join(SoporteCategoria, SoporteTicket.soporte_categoria_id == SoporteCategoria.id)
        .join(Usuario, SoporteTicket.usuario_id == Usuario.id)
        .where(*where_clauses)
        .order_by(SoporteTicket.id.desc())
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                str(item.id),
                item.creado.strftime("%Y-%m-%d %H:%M"),
                item.usuario_email,
                item.soporte_categoria_nombre,
                item.funcionario_email,
                item.departamento,
                item.estado,
                item.descripcion,
            )
    console.print(tabla)
