import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

"""
NetMonitor CLI - Herramienta de análisis de logs de red
"""
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from netmonitor.parser import LogParser
from netmonitor.analyzer import LogAnalyzer
from netmonitor.reporter import Reporter

app = typer.Typer(
    name="netmonitor",
    help="CLI tool for network equipment log analysis",
    add_completion=False,
)
console = Console()


@app.command()
def analyze(
    log_file: Annotated[
        Path,
        typer.Argument(
            help="Path to network log file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output report file (optional)"),
    ] = None,
    format_type: Annotated[
        str,
        typer.Option("--format", "-f", help="Output format: text, json, html"),
    ] = "text",
) -> None:
    """
    Analiza un archivo de logs de equipos de red.
    
    Ejemplo:
        netmonitor analyze sample_logs/network.log
        netmonitor analyze logs/router.log -o report.txt -f text
    """
    console.print(f"[bold blue]Analizando:[/bold blue] {log_file}")
    
    # Parsear logs
    with console.status("[bold green]Parseando logs..."):
        parser = LogParser(log_file)
        entries = parser.parse()
    
    console.print(f"[green]✓[/green] {len(entries)} entradas encontradas")
    
    # Analizar
    with console.status("[bold green]Analizando patrones..."):
        analyzer = LogAnalyzer(entries)
        analysis = analyzer.analyze()
    
    # Generar reporte
    reporter = Reporter(analysis)
    
    if output:
        reporter.save(output, format_type=format_type)
        console.print(f"[green]✓[/green] Reporte guardado en: {output}")
    else:
        reporter.display_console()


@app.command()
def version() -> None:
    """Muestra la versión de NetMonitor."""
    console.print("[bold blue]NetMonitor[/bold blue] v0.1.0")
    console.print("Desarrollado por Pedro Araujo")


@app.command()
def demo() -> None:
    """
    Ejecuta una demo con datos de ejemplo.
    """
    console.print("[bold yellow]Demo Mode[/bold yellow]")
    console.print("Generando logs de ejemplo...\n")
    
    # Crear tabla de ejemplo
    table = Table(title="Análisis de Logs - Demo")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", style="magenta")
    
    table.add_row("Total de Eventos", "1,234")
    table.add_row("Errores Críticos", "5")
    table.add_row("Warnings", "45")
    table.add_row("Período", "2024-10-01 a 2024-10-05")
    
    console.print(table)


def main() -> None:
    """Entry point para la aplicación."""
    app()


if __name__ == "__main__":
    main()
    