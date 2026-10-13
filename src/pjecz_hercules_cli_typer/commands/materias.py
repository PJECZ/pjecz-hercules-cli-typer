"""
Materias
"""

from rich.console import Console
from typer import Exit, Typer

app = Typer(help="Materias")


@app.command()
def consultar():
    """Consultar materias"""
    console = Console()
    console.print("Consultando materias...")
