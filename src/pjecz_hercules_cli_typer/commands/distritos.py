"""
Distritos
"""

from rich.console import Console
from typer import Exit, Typer

app = Typer(help="Distritos")


@app.command()
def consultar():
    """Consultar distritos"""
    console = Console()
    console.print("Consultando distritos...")
