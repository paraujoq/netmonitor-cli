"""
CLI principal de NetMonitor.
"""
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from netmonitor.parser import LogParser
from netmonitor.analyzer import LogAnalyzer
from netmonitor.reporter import Reporter

app = typer.Typer(
    name="netmonitor",
    help="🔍 Network Log Monitoring and Analysis Tool",
    add_completion=False,
)
console = Console()


def version_callback(value: bool) -> None:
    """Muestra la versión y sale."""
    if value:
        rprint("[cyan]NetMonitor CLI[/cyan] version [green]0.1.0[/green]")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """
    NetMonitor CLI - Network Log Analysis Tool.
    
    Analyze network device logs and generate comprehensive reports.
    """
    pass


@app.command()
def analyze(
    log_file: Path = typer.Argument(
        ...,
        help="Path to the log file to analyze",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
    ),
    output: Optional[Path] = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path (default: display in console)",
    ),
    format: str = typer.Option(
        "console",
        "--format",
        "-f",
        help="Output format: console, text, json, html",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress progress messages",
    ),
) -> None:
    """
    Analyze a log file and generate a report.
    
    Examples:
    
        # Analyze and display in console
        netmonitor analyze network.log
        
        # Export to text file
        netmonitor analyze network.log -o report.txt -f text
        
        # Export to JSON
        netmonitor analyze network.log -o report.json -f json
        
        # Export to HTML
        netmonitor analyze network.log -o report.html -f html
    """
    try:
        # Step 1: Parse
        if not quiet:
            console.print(f"\n[cyan]🔍 Parsing log file:[/cyan] {log_file}")
        
        parser = LogParser(log_file)
        entries = parser.parse()
        
        if not entries:
            console.print("[red]❌ No valid log entries found![/red]")
            raise typer.Exit(code=1)
        
        if not quiet:
            console.print(f"[green]✓[/green] Parsed {len(entries)} entries")
            if parser.error_count > 0:
                console.print(
                    f"[yellow]⚠[/yellow] {parser.error_count} lines had parsing errors"
                )
        
        # Step 2: Analyze
        if not quiet:
            console.print("\n[cyan]📊 Analyzing logs...[/cyan]")
        
        analyzer = LogAnalyzer(entries)
        analysis = analyzer.analyze()
        
        if not quiet:
            console.print(
                f"[green]✓[/green] Analysis complete "
                f"(Error rate: {analysis.error_rate:.1f}%)"
            )
        
        # Step 3: Report
        reporter = Reporter(analysis)
        
        if output is None and format == "console":
            # Display in console
            reporter.display_console()
        elif output:
            # Export to file
            if not quiet:
                console.print(f"\n[cyan]💾 Exporting report...[/cyan]")
            
            # Determinar formato por extensión si no se especificó
            if format == "console":
                suffix = output.suffix.lower()
                if suffix == ".json":
                    format = "json"
                elif suffix == ".html":
                    format = "html"
                else:
                    format = "text"
            
            reporter.save(output, format_type=format)
            
            if not quiet:
                console.print(f"[green]✓[/green] Report saved to: [cyan]{output}[/cyan]")
        else:
            console.print("[red]Error:[/red] --output required when using --format")
            raise typer.Exit(code=1)
        
        if not quiet:
            console.print("\n[green]✅ Done![/green]\n")
    
    except FileNotFoundError:
        console.print(f"[red]❌ Error:[/red] File not found: {log_file}")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[red]❌ Error:[/red] {str(e)}")
        if not quiet:
            console.print_exception()
        raise typer.Exit(code=1)


@app.command()
def demo(
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress progress messages",
    ),
) -> None:
    """
    Run a demo analysis with sample log data.
    
    This command analyzes the included sample log file and displays
    the results in the console.
    """
    try:
        # Buscar archivo de demo
        demo_file = Path("sample_logs/network_demo.log")
        
        if not demo_file.exists():
            console.print(
                "[yellow]⚠ Demo file not found.[/yellow]\n"
                "Creating sample log file..."
            )
            _create_demo_file(demo_file)
        
        if not quiet:
            console.print(
                Panel.fit(
                    "[bold cyan]🎬 NetMonitor Demo[/bold cyan]\n"
                    "Analyzing sample network logs...",
                    border_style="cyan",
                )
            )
        
        # Analizar el archivo de demo
        parser = LogParser(demo_file)
        entries = parser.parse()
        
        if not quiet:
            console.print(f"\n[green]✓[/green] Loaded {len(entries)} sample entries")
        
        analyzer = LogAnalyzer(entries)
        analysis = analyzer.analyze()
        
        reporter = Reporter(analysis)
        reporter.display_console()
        
        if not quiet:
            console.print(
                "\n[dim]💡 Tip: Try analyzing your own logs with:[/dim]"
            )
            console.print("[dim]   netmonitor analyze your_log_file.log[/dim]\n")
    
    except Exception as e:
        console.print(f"[red]❌ Demo failed:[/red] {str(e)}")
        raise typer.Exit(code=1)


def _create_demo_file(path: Path) -> None:
    """Crea un archivo de demo si no existe."""
    path.parent.mkdir(parents=True, exist_ok=True)
    
    demo_content = """2024-12-04 08:00:15 INFO [Router-01] System startup complete
2024-12-04 08:01:23 WARNING [Router-01] High CPU usage: 78%
2024-12-04 08:02:10 ERROR [Router-01] Connection timeout to 192.168.1.100
2024-12-04 08:03:12 ERROR [Router-01] Connection timeout to 192.168.1.101
2024-12-04 08:04:45 ERROR [Router-01] BGP peer 10.0.0.1 down
2024-12-04 08:05:15 CRITICAL [Router-01] Memory usage critical: 95%
2024-12-04 08:06:55 ERROR [Switch-02] STP loop detected on port 8
2024-12-04 08:08:45 ERROR [Router-01] Connection timeout to 192.168.1.102
2024-12-04 08:10:25 ERROR [Router-01] OSPF neighbor timeout
2024-12-04 08:11:00 CRITICAL [Firewall-03] Security policy violation detected
2024-12-04 08:12:10 ERROR [Switch-02] Port security violation on port 16
2024-12-04 08:13:55 ERROR [Router-01] Connection timeout to 192.168.1.103
2024-12-04 08:15:40 ERROR [Router-01] Connection timeout to 192.168.1.104
2024-12-04 09:02:35 ERROR [Router-01] Routing protocol failure
2024-12-04 09:04:55 ERROR [Router-01] Connection timeout to 192.168.1.105
2024-12-04 09:07:30 CRITICAL [Router-01] Hardware failure detected
2024-12-04 09:08:45 ERROR [Switch-02] Power supply 2 failed
2024-12-04 08:00:45 INFO [Switch-02] Port 24 link up
2024-12-04 08:02:45 INFO [Firewall-03] Rule #245 applied
2024-12-04 08:05:50 WARNING [Firewall-03] Packet dropped: invalid source
"""
    
    path.write_text(demo_content, encoding="utf-8")
    console.print(f"[green]✓[/green] Created demo file: {path}")


if __name__ == "__main__":
    app()