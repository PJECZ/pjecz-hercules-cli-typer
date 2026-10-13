"""
Autoridades
"""

from rich.console import Console
from typer import Exit, Typer

app = Typer(help="Autoridades")


@app.command()
def consultar():
    """Consultar autoridades"""
    console = Console()
    console.print("Consultando autoridades...")
