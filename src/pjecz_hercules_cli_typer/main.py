"""
Main
"""

from typer import Typer

from pjecz_hercules_cli_typer.commands.autoridades import app as autoridades_app
from pjecz_hercules_cli_typer.commands.distritos import app as distritos_app
from pjecz_hercules_cli_typer.commands.edictos import app as edictos_app
from pjecz_hercules_cli_typer.commands.glosas import app as glosas_app
from pjecz_hercules_cli_typer.commands.listas_de_acuerdos import app as listas_de_acuerdos_app
from pjecz_hercules_cli_typer.commands.materias import app as materias_app
from pjecz_hercules_cli_typer.commands.materias_tipos_juicios import app as materias_tipos_de_juicios_app
from pjecz_hercules_cli_typer.commands.modulos import app as modulos_app
from pjecz_hercules_cli_typer.commands.ofi_documentos import app as ofi_documentos_app
from pjecz_hercules_cli_typer.commands.permisos import app as permisos_app
from pjecz_hercules_cli_typer.commands.roles import app as roles_app
from pjecz_hercules_cli_typer.commands.sentencias import app as sentencias_app
from pjecz_hercules_cli_typer.commands.usuarios import app as usuarios_app
from pjecz_hercules_cli_typer.commands.usuarios_roles import app as usuarios_roles_app

app = Typer()
app.add_typer(autoridades_app, name="autoridades")
app.add_typer(distritos_app, name="distritos")
app.add_typer(edictos_app, name="edictos")
app.add_typer(glosas_app, name="glosas")
app.add_typer(listas_de_acuerdos_app, name="listas-de-acuerdos")
app.add_typer(materias_app, name="materias")
app.add_typer(materias_tipos_de_juicios_app, name="materias-tipos-de-juicios")
app.add_typer(modulos_app, name="modulos")
app.add_typer(ofi_documentos_app, name="ofi-documentos")
app.add_typer(permisos_app, name="permisos")
app.add_typer(roles_app, name="roles")
app.add_typer(sentencias_app, name="sentencias")
app.add_typer(usuarios_app, name="usuarios")
app.add_typer(usuarios_roles_app, name="usuarios-roles")

if __name__ == "__main__":
    app()
