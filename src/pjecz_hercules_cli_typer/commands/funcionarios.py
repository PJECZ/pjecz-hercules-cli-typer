"""
Funcionarios
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_curp, safe_email, safe_string
from pjecz_hercules_cli_typer.models.funcionarios import Funcionario

app = Typer(help="Funcionarios")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    nombres: str | None = None,
    apellido_paterno: str | None = None,
    apellido_materno: str | None = None,
    curp: str | None = None,
    email: str | None = None,
    puesto: str | None = None,
    en_funciones: bool | None = None,
    en_soportes: bool | None = None,
):
    """Consultar funcionarios"""
    console = Console()
    console.print("Consultando funcionarios...")

    # Preparar tabla
    tabla = Table(title="Funcionarios")
    tabla.add_column("Nombres", header_style="green")
    tabla.add_column("Apellido paterno", header_style="green")
    tabla.add_column("Apellido materno", header_style="green")
    tabla.add_column("CURP", header_style="green", no_wrap=True)
    tabla.add_column("Email", header_style="green", no_wrap=True)
    tabla.add_column("Puesto", header_style="green")
    tabla.add_column("En funciones", header_style="green")
    tabla.add_column("En soportes", header_style="green")

    # Cláusulas where
    where_clauses = [Funcionario.estatus == "A"]
    if nombres and (nombres := safe_string(nombres)):
        where_clauses.append(Funcionario.nombres.like("%" + nombres + "%"))
    if apellido_paterno and (apellido_paterno := safe_string(apellido_paterno)):
        where_clauses.append(Funcionario.apellido_paterno.like("%" + apellido_paterno + "%"))
    if apellido_materno and (apellido_materno := safe_string(apellido_materno)):
        where_clauses.append(Funcionario.apellido_materno.like("%" + apellido_materno + "%"))
    if curp and (curp := safe_curp(curp)):
        where_clauses.append(Funcionario.curp == curp)
    if email and (email := safe_email(email)):
        where_clauses.append(Funcionario.email == email)
    if puesto and (puesto := safe_string(puesto)):
        where_clauses.append(Funcionario.puesto.like("%" + puesto + "%"))
    if en_funciones is not None:
        where_clauses.append(Funcionario.en_funciones == en_funciones)
    if en_soportes is not None:
        where_clauses.append(Funcionario.en_soportes == en_soportes)

    # Sentencia
    stmt = (
        select(
            Funcionario.nombres,
            Funcionario.apellido_paterno,
            Funcionario.apellido_materno,
            Funcionario.curp,
            Funcionario.email,
            Funcionario.puesto,
            Funcionario.en_funciones,
            Funcionario.en_soportes,
        )
        .where(*where_clauses)
        .order_by(Funcionario.apellido_paterno, Funcionario.apellido_materno, Funcionario.nombres)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.nombres,
                item.apellido_paterno,
                item.apellido_materno,
                item.curp,
                item.email,
                item.puesto,
                "Sí" if item.en_funciones else "No",
                "Sí" if item.en_soportes else "No",
            )
    console.print(tabla)
