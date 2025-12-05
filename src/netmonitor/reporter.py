"""
Generador de reportes en múltiples formatos.
"""
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from netmonitor.analyzer import LogAnalysis


class Reporter:
    """
    Genera reportes del análisis en diferentes formatos.
    """
    
    def __init__(self, analysis: LogAnalysis) -> None:
        """
        Inicializa el reporter.
        
        Args:
            analysis: Resultados del análisis de logs
        """
        self.analysis = analysis
        self.console = Console()
    
    def display_console(self) -> None:
        """Muestra el reporte en la consola con formato Rich."""
        self.console.print()
        self.console.print(
            Panel.fit(
                "[bold cyan]📊 Network Log Analysis Report[/bold cyan]",
                border_style="cyan"
            )
        )
        self.console.print()
        
        # Resumen general
        self._display_summary()
        
        # Distribución por nivel con gráfico
        self._display_level_distribution()
        
        # Top dispositivos
        self._display_top_devices()
        
        # Top errores
        self._display_top_errors()
        
        # Dispositivos con más errores
        self._display_error_devices()
        
        # Distribución horaria
        self._display_hourly_distribution()
        
        # Eventos críticos
        if self.analysis.critical_events:
            self._display_critical_events()
    
    def _display_summary(self) -> None:
        """Muestra resumen general con colores según severidad."""
        start, end = self.analysis.date_range
        
        # Tabla de resumen
        table = Table(
            box=box.ROUNDED,
            show_header=False,
            title="📋 Summary",
            title_style="bold cyan"
        )
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        
        # Total entries
        table.add_row("Total Entries", f"{self.analysis.total_entries:,}")
        
        # Time range
        duration_str = self._format_duration()
        table.add_row(
            "Time Range",
            f"{start.strftime('%Y-%m-%d %H:%M')} → {end.strftime('%H:%M')}"
        )
        table.add_row("Duration", duration_str)
        
        # Error rate con color
        error_rate = self.analysis.error_rate
        rate_color = self._get_severity_color(error_rate)
        rate_emoji = "🔴" if error_rate > 20 else "🟡" if error_rate > 5 else "🟢"
        table.add_row(
            "Error Rate",
            f"[{rate_color}]{error_rate:.1f}%[/{rate_color}] {rate_emoji}"
        )
        
        self.console.print(table)
        self.console.print()
    
    def _display_level_distribution(self) -> None:
        """Muestra distribución por nivel con gráfico de barras."""
        if not self.analysis.level_distribution:
            return
        
        self.console.print("[bold cyan]📊 Level Distribution[/bold cyan]")
        self.console.print()
        
        # Ordenar por severidad: CRITICAL, ERROR, WARNING, INFO, DEBUG
        severity_order = {"CRITICAL": 0, "ERROR": 1, "WARNING": 2, "INFO": 3, "DEBUG": 4}
        sorted_levels = sorted(
            self.analysis.level_distribution.items(),
            key=lambda x: severity_order.get(x[0], 99)
        )
        
        total = self.analysis.total_entries
        max_count = max(self.analysis.level_distribution.values())
        
        for level, count in sorted_levels:
            percentage = (count / total * 100)
            
            # Color según nivel
            color = self._get_level_color(level)
            emoji = self._get_level_emoji(level)
            
            # Barra visual (máximo 40 caracteres)
            bar_length = int((count / max_count) * 40)
            bar = "█" * bar_length
            
            # Formato: EMOJI LEVEL BAR COUNT (PERCENTAGE)
            level_text = Text()
            level_text.append(f"{emoji} ", style="white")
            level_text.append(f"{level:8}", style=f"bold {color}")
            level_text.append(f" {bar}", style=color)
            level_text.append(f" {count:4} ", style="white")
            level_text.append(f"({percentage:5.1f}%)", style="dim white")
            
            self.console.print(level_text)
        
        self.console.print()
    
    def _display_top_devices(self) -> None:
        """Muestra top dispositivos por actividad."""
        if not self.analysis.device_distribution:
            return
        
        table = Table(
            title="📱 Top Devices by Activity",
            box=box.SIMPLE,
            show_header=True
        )
        table.add_column("#", style="dim", width=3, justify="right")
        table.add_column("Device", style="cyan")
        table.add_column("Events", justify="right", style="magenta")
        table.add_column("Bar", style="blue")
        
        max_count = max(self.analysis.device_distribution.values())
        
        for idx, (device, count) in enumerate(
            list(self.analysis.device_distribution.items())[:5], start=1
        ):
            bar_length = int((count / max_count) * 20)
            bar = "█" * bar_length
            
            table.add_row(
                str(idx),
                device,
                str(count),
                bar
            )
        
        self.console.print(table)
        self.console.print()
    
    def _display_top_errors(self) -> None:
        """Muestra los errores más frecuentes."""
        if not self.analysis.top_errors:
            return
        
        table = Table(
            title="🔴 Top 5 Most Frequent Errors",
            box=box.ROUNDED,
            show_lines=True
        )
        table.add_column("#", style="dim", width=3)
        table.add_column("Error Message", style="yellow")
        table.add_column("Count", justify="right", style="red bold", width=8)
        
        for idx, (message, count) in enumerate(self.analysis.top_errors, start=1):
            # Truncar mensaje si es muy largo
            display_msg = message[:70] + "..." if len(message) > 70 else message
            table.add_row(str(idx), display_msg, str(count))
        
        self.console.print(table)
        self.console.print()
    
    def _display_error_devices(self) -> None:
        """Muestra dispositivos con más errores."""
        if not self.analysis.errors_by_device:
            self.console.print("[dim]No errors found[/dim]")
            self.console.print()
            return
        
        table = Table(
            title="⚠️  Devices with Most Errors",
            box=box.SIMPLE
        )
        table.add_column("Device", style="cyan")
        table.add_column("Errors", justify="right", style="red bold")
        table.add_column("Visual", style="red")
        
        max_errors = max(self.analysis.errors_by_device.values())
        
        for device, count in list(self.analysis.errors_by_device.items())[:5]:
            bar_length = int((count / max_errors) * 15)
            bar = "▓" * bar_length
            table.add_row(device, str(count), bar)
        
        self.console.print(table)
        self.console.print()
    
    def _display_hourly_distribution(self) -> None:
        """Muestra distribución de eventos por hora."""
        if not self.analysis.hourly_distribution:
            return
        
        self.console.print("[bold cyan]⏰ Hourly Distribution[/bold cyan]")
        self.console.print()
        
        max_count = max(self.analysis.hourly_distribution.values())
        
        for hour in range(24):
            count = self.analysis.hourly_distribution.get(hour, 0)
            if count == 0:
                continue
            
            # Barra proporcional
            bar_length = int((count / max_count) * 30)
            bar = "█" * bar_length
            
            # Color según volumen
            color = "red" if count > max_count * 0.7 else "yellow" if count > max_count * 0.4 else "green"
            
            hour_text = Text()
            hour_text.append(f"{hour:02d}:00 ", style="cyan")
            hour_text.append(bar, style=color)
            hour_text.append(f" {count}", style="white")
            
            self.console.print(hour_text)
        
        self.console.print()
    
    def _display_critical_events(self) -> None:
        """Muestra eventos críticos."""
        table = Table(
            title="🚨 Critical Events",
            box=box.HEAVY,
            show_lines=True,
            border_style="red"
        )
        table.add_column("Timestamp", style="red bold")
        table.add_column("Device", style="yellow")
        table.add_column("Message", style="white")
        
        for event in self.analysis.critical_events[:10]:
            table.add_row(
                event.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                event.device,
                event.message[:60] + "..." if len(event.message) > 60 else event.message
            )
        
        self.console.print(table)
        self.console.print()
    
    def _format_duration(self) -> str:
        """Formatea la duración en formato legible."""
        hours = self.analysis.duration_hours
        if hours < 1:
            return f"{int(hours * 60)} minutes"
        elif hours < 24:
            return f"{hours:.1f} hours"
        else:
            days = hours / 24
            return f"{days:.1f} days"
    
    def _get_severity_color(self, error_rate: float) -> str:
        """Retorna color según tasa de error."""
        if error_rate > 20:
            return "red"
        elif error_rate > 10:
            return "yellow"
        elif error_rate > 5:
            return "orange1"
        else:
            return "green"
    
    def _get_level_color(self, level: str) -> str:
        """Retorna color según nivel de log."""
        colors = {
            "CRITICAL": "red bold",
            "ERROR": "red",
            "WARNING": "yellow",
            "INFO": "blue",
            "DEBUG": "dim white"
        }
        return colors.get(level, "white")
    
    def _get_level_emoji(self, level: str) -> str:
        """Retorna emoji según nivel de log."""
        emojis = {
            "CRITICAL": "🚨",
            "ERROR": "🔴",
            "WARNING": "🟡",
            "INFO": "🔵",
            "DEBUG": "⚪"
        }
        return emojis.get(level, "•")
    
    def save(self, output_path: Path, format_type: str = "text") -> None:
        """
        Guarda el reporte en un archivo.
        
        Args:
            output_path: Ruta del archivo de salida
            format_type: Formato del reporte (text, json, html)
        """
        if format_type == "json":
            self._save_json(output_path)
        elif format_type == "html":
            self._save_html(output_path)
        else:
            self._save_text(output_path)
        
        self.console.print(f"\n[green]✓[/green] Report saved to: [cyan]{output_path}[/cyan]")
    
    def _save_text(self, path: Path) -> None:
        """Guarda reporte en formato texto plano."""
        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 70 + "\n")
            f.write("NETWORK LOG ANALYSIS REPORT\n")
            f.write("=" * 70 + "\n\n")
            
            start, end = self.analysis.date_range
            f.write(f"Total Entries: {self.analysis.total_entries:,}\n")
            f.write(f"Time Range: {start} → {end}\n")
            f.write(f"Duration: {self._format_duration()}\n")
            f.write(f"Error Rate: {self.analysis.error_rate:.2f}%\n\n")
            
            f.write("LEVEL DISTRIBUTION:\n")
            f.write("-" * 70 + "\n")
            for level, count in sorted(
                self.analysis.level_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                pct = (count / self.analysis.total_entries * 100)
                f.write(f"  {level:10} {count:6,} ({pct:5.1f}%)\n")
            
            if self.analysis.errors_by_device:
                f.write("\nDEVICES WITH ERRORS:\n")
                f.write("-" * 70 + "\n")
                for device, count in list(self.analysis.errors_by_device.items())[:10]:
                    f.write(f"  {device:30} {count:4} errors\n")
            
            if self.analysis.top_errors:
                f.write("\nTOP ERRORS:\n")
                f.write("-" * 70 + "\n")
                for idx, (msg, count) in enumerate(self.analysis.top_errors, 1):
                    f.write(f"  {idx}. [{count}x] {msg}\n")
    
    def _save_json(self, path: Path) -> None:
        """Guarda reporte en formato JSON."""
        start, end = self.analysis.date_range
        
        data = {
            "summary": {
                "total_entries": self.analysis.total_entries,
                "date_range": {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
                "duration_hours": round(self.analysis.duration_hours, 2),
                "error_rate": round(self.analysis.error_rate, 2),
            },
            "level_distribution": self.analysis.level_distribution,
            "device_distribution": dict(list(self.analysis.device_distribution.items())[:20]),
            "top_errors": [
                {"message": msg, "count": cnt} 
                for msg, cnt in self.analysis.top_errors
            ],
            "errors_by_device": self.analysis.errors_by_device,
            "hourly_distribution": self.analysis.hourly_distribution,
            "critical_events_count": len(self.analysis.critical_events),
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_html(self, path: Path) -> None:
        """Guarda reporte en formato HTML mejorado."""
        start, end = self.analysis.date_range
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Log Analysis Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .content {{ padding: 30px; }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        .stat-card h3 {{
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 10px;
        }}
        .stat-card .value {{
            font-size: 2em;
            font-weight: bold;
            color: #495057;
        }}
        h2 {{
            color: #495057;
            margin: 40px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        table {{ 
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .error-rate {{
            color: #dc3545;
            font-weight: bold;
            font-size: 1.2em;
        }}
        .bar {{
            height: 20px;
            background: #667eea;
            border-radius: 10px;
            transition: width 0.3s ease;
        }}
        footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            margin-top: 40px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Network Log Analysis</h1>
            <p>Generated by NetMonitor CLI</p>
        </header>
        
        <div class="content">
            <div class="summary-grid">
                <div class="stat-card">
                    <h3>Total Entries</h3>
                    <div class="value">{self.analysis.total_entries:,}</div>
                </div>
                <div class="stat-card">
                    <h3>Duration</h3>
                    <div class="value">{self._format_duration()}</div>
                </div>
                <div class="stat-card">
                    <h3>Error Rate</h3>
                    <div class="value error-rate">{self.analysis.error_rate:.1f}%</div>
                </div>
                <div class="stat-card">
                    <h3>Time Range</h3>
                    <div class="value" style="font-size: 1.2em;">{start.strftime('%H:%M')} → {end.strftime('%H:%M')}</div>
                </div>
            </div>
            
            <h2>📊 Level Distribution</h2>
            <table>
                <thead>
                    <tr><th>Level</th><th>Count</th><th>Percentage</th><th>Visual</th></tr>
                </thead>
                <tbody>
                    {''.join(f'''<tr>
                        <td><strong>{lvl}</strong></td>
                        <td>{cnt:,}</td>
                        <td>{cnt/self.analysis.total_entries*100:.1f}%</td>
                        <td><div class="bar" style="width: {cnt/self.analysis.total_entries*100}%"></div></td>
                    </tr>''' 
                    for lvl, cnt in sorted(self.analysis.level_distribution.items(), 
                                          key=lambda x: x[1], reverse=True))}
                </tbody>
            </table>
            
            <h2>⚠️ Top Devices with Errors</h2>
            <table>
                <thead>
                    <tr><th>Device</th><th>Errors</th></tr>
                </thead>
                <tbody>
                    {''.join(f'<tr><td>{dev}</td><td style="color: #dc3545; font-weight: bold;">{cnt}</td></tr>' 
                            for dev, cnt in list(self.analysis.errors_by_device.items())[:10])}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p><strong>NetMonitor CLI</strong> - Network Log Analysis Tool</p>
            <p style="font-size: 0.9em; margin-top: 10px;">
                Report generated on {start.strftime('%Y-%m-%d at %H:%M:%S')}
            </p>
        </footer>
    </div>
</body>
</html>"""
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)