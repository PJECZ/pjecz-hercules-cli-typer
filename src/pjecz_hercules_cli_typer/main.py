"""
Main
"""

from typer import Typer

from pjecz_hercules_cli_typer.commands.autoridades import app as autoridades_app
from pjecz_hercules_cli_typer.commands.distritos import app as distritos_app
from pjecz_hercules_cli_typer.commands.edictos import app as edictos_app
from pjecz_hercules_cli_typer.commands.materias import app as materias_app
from pjecz_hercules_cli_typer.commands.modulos import app as modulos_app
from pjecz_hercules_cli_typer.commands.permisos import app as permisos_app
from pjecz_hercules_cli_typer.commands.roles import app as roles_app
from pjecz_hercules_cli_typer.commands.usuarios import app as usuarios_app
from pjecz_hercules_cli_typer.commands.usuarios_roles import app as usuarios_roles_app

app = Typer()
app.add_typer(autoridades_app, name="autoridades")
app.add_typer(distritos_app, name="distritos")
app.add_typer(edictos_app, name="edictos")
app.add_typer(materias_app, name="materias")
app.add_typer(modulos_app, name="modulos")
app.add_typer(permisos_app, name="permisos")
app.add_typer(roles_app, name="roles")
app.add_typer(usuarios_app, name="usuarios")
app.add_typer(usuarios_roles_app, name="usuarios-roles")

if __name__ == "__main__":
    app()
