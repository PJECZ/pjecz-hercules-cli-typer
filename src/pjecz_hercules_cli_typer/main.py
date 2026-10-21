"""
Main
"""

import sys

from rich.console import Console
from typer import Typer

from pjecz_hercules_cli_typer.commands.arc_documentos import app as arc_documentos_app
from pjecz_hercules_cli_typer.commands.arc_documentos_tipos import app as arc_documentos_tipos_app
from pjecz_hercules_cli_typer.commands.arc_juzgados_extintos import app as arc_juzgados_extintos_app
from pjecz_hercules_cli_typer.commands.arc_remesas import app as arc_remesas_app
from pjecz_hercules_cli_typer.commands.arc_remesas_documentos import app as arc_remesas_documentos_app
from pjecz_hercules_cli_typer.commands.autoridades import app as autoridades_app
from pjecz_hercules_cli_typer.commands.dgt_depositos import app as dgt_depositos_app
from pjecz_hercules_cli_typer.commands.dgt_plataformas import app as dgt_plataformas_app
from pjecz_hercules_cli_typer.commands.dgt_rutas import app as dgt_rutas_app
from pjecz_hercules_cli_typer.commands.dgt_tipos import app as dgt_tipos_app
from pjecz_hercules_cli_typer.commands.distritos import app as distritos_app
from pjecz_hercules_cli_typer.commands.domicilios import app as domicilios_app
from pjecz_hercules_cli_typer.commands.edictos import app as edictos_app
from pjecz_hercules_cli_typer.commands.estados import app as estados_app
from pjecz_hercules_cli_typer.commands.funcionarios import app as funcionarios_app
from pjecz_hercules_cli_typer.commands.funcionarios_oficinas import app as funcionarios_oficinas_app
from pjecz_hercules_cli_typer.commands.glosas import app as glosas_app
from pjecz_hercules_cli_typer.commands.listas_de_acuerdos import app as listas_de_acuerdos_app
from pjecz_hercules_cli_typer.commands.materias import app as materias_app
from pjecz_hercules_cli_typer.commands.materias_tipos_juicios import app as materias_tipos_de_juicios_app
from pjecz_hercules_cli_typer.commands.modulos import app as modulos_app
from pjecz_hercules_cli_typer.commands.municipios import app as municipios_app
from pjecz_hercules_cli_typer.commands.ofi_documentos import app as ofi_documentos_app
from pjecz_hercules_cli_typer.commands.ofi_documentos_destinatarios import app as ofi_documentos_destinatarios_app
from pjecz_hercules_cli_typer.commands.oficinas import app as oficinas_app
from pjecz_hercules_cli_typer.commands.permisos import app as permisos_app
from pjecz_hercules_cli_typer.commands.roles import app as roles_app
from pjecz_hercules_cli_typer.commands.sentencias import app as sentencias_app
from pjecz_hercules_cli_typer.commands.soportes_categorias import app as soportes_categorias_app
from pjecz_hercules_cli_typer.commands.soportes_tickets import app as soportes_tickets_app
from pjecz_hercules_cli_typer.commands.usuarios import app as usuarios_app
from pjecz_hercules_cli_typer.commands.usuarios_roles import app as usuarios_roles_app
from pjecz_hercules_cli_typer.core.exceptions import MyNotValidParamError

app = Typer()
app.add_typer(arc_documentos_app, name="arc-documentos")
app.add_typer(arc_documentos_tipos_app, name="arc-documentos-tipos")
app.add_typer(arc_juzgados_extintos_app, name="arc-juzgados-extintos")
app.add_typer(arc_remesas_app, name="arc-remesas")
app.add_typer(arc_remesas_documentos_app, name="arc-remesas-documentos")
app.add_typer(autoridades_app, name="autoridades")
app.add_typer(dgt_depositos_app, name="dgt-depositos")
app.add_typer(dgt_plataformas_app, name="dgt-plataformas")
app.add_typer(dgt_rutas_app, name="dgt-rutas")
app.add_typer(dgt_tipos_app, name="dgt-tipos")
app.add_typer(distritos_app, name="distritos")
app.add_typer(domicilios_app, name="domicilios")
app.add_typer(edictos_app, name="edictos")
app.add_typer(estados_app, name="estados")
app.add_typer(funcionarios_app, name="funcionarios")
app.add_typer(funcionarios_oficinas_app, name="funcionarios-oficinas")
app.add_typer(glosas_app, name="glosas")
app.add_typer(listas_de_acuerdos_app, name="listas-de-acuerdos")
app.add_typer(materias_app, name="materias")
app.add_typer(materias_tipos_de_juicios_app, name="materias-tipos-de-juicios")
app.add_typer(modulos_app, name="modulos")
app.add_typer(municipios_app, name="municipios")
app.add_typer(ofi_documentos_app, name="ofi-documentos")
app.add_typer(ofi_documentos_destinatarios_app, name="ofi-documentos-destinatarios")
app.add_typer(oficinas_app, name="oficinas")
app.add_typer(permisos_app, name="permisos")
app.add_typer(roles_app, name="roles")
app.add_typer(sentencias_app, name="sentencias")
app.add_typer(soportes_categorias_app, name="soportes-categorias")
app.add_typer(soportes_tickets_app, name="soportes-tickets")
app.add_typer(usuarios_app, name="usuarios")
app.add_typer(usuarios_roles_app, name="usuarios-roles")


def main():
    """Ejecutar la aplicación y mostrar los parámetros inválidos sin traceback"""
    try:
        app()
    except MyNotValidParamError as error:
        Console(stderr=True).print(f"[red]{error}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
