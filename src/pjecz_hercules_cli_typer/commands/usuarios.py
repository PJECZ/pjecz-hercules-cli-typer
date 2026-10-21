"""
Usuarios
"""

from rich.console import Console
from rich.table import Table
from sqlalchemy import select
from typer import Typer

from pjecz_hercules_cli_typer.core.database import session_scope
from pjecz_hercules_cli_typer.core.validations import safe_clave, safe_curp, safe_email, safe_string
from pjecz_hercules_cli_typer.models.autoridades import Autoridad
from pjecz_hercules_cli_typer.models.distritos import Distrito
from pjecz_hercules_cli_typer.models.usuarios import Usuario

app = Typer(help="Usuarios")


@app.command()
def consultar(
    offset: int = 0,
    limit: int = 25,
    email: str | None = None,
    nombres: str | None = None,
    apellido_paterno: str | None = None,
    apellido_materno: str | None = None,
    curp: str | None = None,
    distrito_clave: str | None = None,
    autoridad_clave: str | None = None,
    puesto: str | None = None,
):
    """Consultar usuarios"""
    console = Console()
    console.print("Consultando usuarios...")

    # Preparar tabla
    tabla = Table(title="Usuarios")
    tabla.add_column("Email", header_style="green", no_wrap=True)
    tabla.add_column("Nombres", header_style="green")
    tabla.add_column("A. Paterno", header_style="green")
    tabla.add_column("A. Materno", header_style="green")
    tabla.add_column("CURP", header_style="green")
    tabla.add_column("Distrito", header_style="green")
    tabla.add_column("Autoridad", header_style="green")
    tabla.add_column("Puesto", header_style="green")

    # Cláusulas where
    where_clauses = [Usuario.estatus == "A"]
    if email and (email := safe_email(email)):
        where_clauses.append(Usuario.email == email)
    if nombres and (nombres := safe_string(nombres)):
        where_clauses.append(Usuario.nombres.like("%" + nombres + "%"))
    if apellido_paterno and (apellido_paterno := safe_string(apellido_paterno)):
        where_clauses.append(Usuario.apellido_paterno.like("%" + apellido_paterno + "%"))
    if apellido_materno and (apellido_materno := safe_string(apellido_materno)):
        where_clauses.append(Usuario.apellido_materno.like("%" + apellido_materno + "%"))
    if curp and (curp := safe_curp(curp)):
        where_clauses.append(Usuario.curp == curp)
    if distrito_clave and (distrito_clave := safe_clave(distrito_clave)):
        where_clauses.append(Distrito.clave == distrito_clave)
    if autoridad_clave and (autoridad_clave := safe_clave(autoridad_clave)):
        where_clauses.append(Autoridad.clave == autoridad_clave)
    if puesto and (puesto := safe_string(puesto)):
        where_clauses.append(Usuario.puesto.like("%" + puesto + "%"))

    # Sentencia
    stmt = (
        select(
            Usuario.email,
            Usuario.nombres,
            Usuario.apellido_paterno,
            Usuario.apellido_materno,
            Usuario.curp,
            Distrito.clave.label("distrito_clave"),
            Autoridad.clave.label("autoridad_clave"),
            Usuario.puesto,
        )
        .select_from(Usuario)
        .join(Autoridad, Usuario.autoridad_id == Autoridad.id)
        .join(Distrito, Autoridad.distrito_id == Distrito.id)
        .where(*where_clauses)
        .order_by(Usuario.email)
        .offset(offset)
        .limit(limit)
    )

    # Consultar, agregar a la tabla y mostrar
    with session_scope() as session:
        for item in session.execute(stmt).all():
            tabla.add_row(
                item.email,
                item.nombres,
                item.apellido_paterno,
                item.apellido_materno,
                item.curp,
                item.distrito_clave,
                item.autoridad_clave,
                item.puesto,
            )
    console.print(tabla)
