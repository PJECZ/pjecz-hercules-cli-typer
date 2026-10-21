"""
Funcionarios Oficinas
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_curp, safe_email
from pjecz_hercules_cli_typer.models.funcionarios import Funcionario
from pjecz_hercules_cli_typer.models.funcionarios_oficinas import FuncionarioOficina
from pjecz_hercules_cli_typer.models.oficinas import Oficina

app = Typer(help="Funcionarios Oficinas")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    funcionario_curp: str | None = None,
    funcionario_email: str | None = None,
    oficina_clave: str | None = None,
):
    """Consultar oficinas de los funcionarios"""
    console = Console()
    console.print("Consultando oficinas de los funcionarios...")

    # Preparar tabla
    tabla = Table(title="Funcionarios Oficinas")
    tabla.add_column("Funcionario email", header_style="green", no_wrap=True)
    tabla.add_column("Oficina", header_style="green", no_wrap=True)
    tabla.add_column("Descripción", header_style="green")

    # Cláusulas where
    where_clauses = [FuncionarioOficina.estatus == "A", Funcionario.estatus == "A", Oficina.estatus == "A"]
    if funcionario_curp and (funcionario_curp := safe_curp(funcionario_curp)):
        where_clauses.append(Funcionario.curp == funcionario_curp)
    if funcionario_email and (funcionario_email := safe_email(funcionario_email)):
        where_clauses.append(Funcionario.email == funcionario_email)
    if oficina_clave and (oficina_clave := safe_clave(oficina_clave, max_len=32)):
        where_clauses.append(Oficina.clave == oficina_clave)

    # Sentencia
    stmt = (
        select(
            Funcionario.email.label("funcionario_email"),
            Oficina.clave.label("oficina_clave"),
            FuncionarioOficina.descripcion,
        )
        .select_from(FuncionarioOficina)
        .join(Funcionario, FuncionarioOficina.funcionario_id == Funcionario.id)
        .join(Oficina, FuncionarioOficina.oficina_id == Oficina.id)
        .where(*where_clauses)
        .order_by(Funcionario.email, Oficina.clave)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(item.funcionario_email, item.oficina_clave, item.descripcion)
    console.print(tabla)
