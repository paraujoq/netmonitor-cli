"""
Generador de reportes en múltiples formatos.
"""
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

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
        self.console.print("\n[bold blue]📊 Reporte de Análisis de Logs[/bold blue]\n")
        
        # Resumen general
        self._display_summary()
        
        # Distribución por nivel
        self._display_level_distribution()
        
        # Top errores
        self._display_top_errors()
        
        # Dispositivos con más errores
        self._display_error_devices()
        
        # Eventos críticos
        if self.analysis.critical_events:
            self._display_critical_events()
    
    def _display_summary(self) -> None:
        """Muestra resumen general."""
        start, end = self.analysis.date_range
        
        summary_text = f"""
[cyan]Total de Entradas:[/cyan] {self.analysis.total_entries:,}
[cyan]Período:[/cyan] {start.strftime('%Y-%m-%d %H:%M')} → {end.strftime('%Y-%m-%d %H:%M')}
[cyan]Duración:[/cyan] {self.analysis.duration_hours:.1f} horas
[cyan]Tasa de Errores:[/cyan] {self.analysis.error_rate:.2f}%
        """
        
        self.console.print(Panel(summary_text.strip(), title="Resumen General"))
        self.console.print()
    
    def _display_level_distribution(self) -> None:
        """Muestra distribución por nivel de severidad."""
        table = Table(title="Distribución por Nivel")
        table.add_column("Nivel", style="cyan")
        table.add_column("Cantidad", justify="right", style="magenta")
        table.add_column("Porcentaje", justify="right", style="green")
        
        for level, count in sorted(
            self.analysis.level_distribution.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            pct = (count / self.analysis.total_entries * 100)
            table.add_row(
                level,
                f"{count:,}",
                f"{pct:.1f}%"
            )
        
        self.console.print(table)
        self.console.print()
    
    def _display_top_errors(self) -> None:
        """Muestra los errores más frecuentes."""
        if not self.analysis.top_errors:
            return
        
        table = Table(title="Top 5 Errores Más Frecuentes")
        table.add_column("#", style="cyan", width=3)
        table.add_column("Mensaje", style="yellow")
        table.add_column("Ocurrencias", justify="right", style="red")
        
        for idx, (message, count) in enumerate(self.analysis.top_errors, start=1):
            table.add_row(
                str(idx),
                message[:80] + "..." if len(message) > 80 else message,
                str(count)
            )
        
        self.console.print(table)
        self.console.print()
    
    def _display_error_devices(self) -> None:
        """Muestra dispositivos con más errores."""
        if not self.analysis.errors_by_device:
            return
        
        table = Table(title="Dispositivos con Más Errores")
        table.add_column("Dispositivo", style="cyan")
        table.add_column("Errores", justify="right", style="red")
        
        for device, count in list(self.analysis.errors_by_device.items())[:5]:
            table.add_row(device, str(count))
        
        self.console.print(table)
        self.console.print()
    
    def _display_critical_events(self) -> None:
        """Muestra eventos críticos."""
        table = Table(title="⚠️  Eventos Críticos", show_lines=True)
        table.add_column("Timestamp", style="red")
        table.add_column("Dispositivo", style="yellow")
        table.add_column("Mensaje", style="white")
        
        for event in self.analysis.critical_events[:10]:  # Máximo 10
            table.add_row(
                event.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                event.device,
                event.message[:60] + "..." if len(event.message) > 60 else event.message
            )
        
        self.console.print(table)
        self.console.print()
    
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
    
    def _save_text(self, path: Path) -> None:
        """Guarda reporte en formato texto plano."""
        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("REPORTE DE ANÁLISIS DE LOGS\n")
            f.write("=" * 60 + "\n\n")
            
            start, end = self.analysis.date_range
            f.write(f"Total de entradas: {self.analysis.total_entries:,}\n")
            f.write(f"Período: {start} → {end}\n")
            f.write(f"Tasa de errores: {self.analysis.error_rate:.2f}%\n\n")
            
            f.write("Distribución por nivel:\n")
            for level, count in self.analysis.level_distribution.items():
                f.write(f"  {level}: {count:,}\n")
    
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
                "error_rate": round(self.analysis.error_rate, 2),
            },
            "level_distribution": self.analysis.level_distribution,
            "device_distribution": self.analysis.device_distribution,
            "top_errors": [
                {"message": msg, "count": cnt} 
                for msg, cnt in self.analysis.top_errors
            ],
        }
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _save_html(self, path: Path) -> None:
        """Guarda reporte en formato HTML básico."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Reporte de Logs</title>
    <meta charset="UTF-8">
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{ 
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        table {{ 
            border-collapse: collapse; 
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{ 
            border: 1px solid #ddd; 
            padding: 12px; 
            text-align: left; 
        }}
        th {{ 
            background-color: #3498db; 
            color: white;
            font-weight: bold;
        }}
        tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        tr:hover {{
            background-color: #e8f4f8;
        }}
        .summary {{
            background-color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .summary p {{
            margin: 8px 0;
            font-size: 16px;
        }}
        .error-rate {{
            color: #e74c3c;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Reporte de Análisis de Logs</h1>
        
        <div class="summary">
            <p><strong>Total de entradas:</strong> {self.analysis.total_entries:,}</p>
            <p><strong>Período:</strong> {self.analysis.date_range[0].strftime('%Y-%m-%d %H:%M')} → {self.analysis.date_range[1].strftime('%Y-%m-%d %H:%M')}</p>
            <p><strong>Duración:</strong> {self.analysis.duration_hours:.1f} horas</p>
            <p><strong>Tasa de errores:</strong> <span class="error-rate">{self.analysis.error_rate:.2f}%</span></p>
        </div>
        
        <h2>Distribución por Nivel</h2>
        <table>
            <tr>
                <th>Nivel</th>
                <th>Cantidad</th>
                <th>Porcentaje</th>
            </tr>
            {''.join(f'<tr><td>{lvl}</td><td>{cnt:,}</td><td>{cnt/self.analysis.total_entries*100:.1f}%</td></tr>' 
                     for lvl, cnt in sorted(self.analysis.level_distribution.items(), key=lambda x: x[1], reverse=True))}
        </table>
        
        <h2>Top Dispositivos con Errores</h2>
        <table>
            <tr>
                <th>Dispositivo</th>
                <th>Errores</th>
            </tr>
            {''.join(f'<tr><td>{dev}</td><td>{cnt}</td></tr>' 
                     for dev, cnt in list(self.analysis.errors_by_device.items())[:10])}
        </table>
        
        <footer style="margin-top: 40px; text-align: center; color: #7f8c8d; font-size: 14px;">
            <p>Generado por NetMonitor CLI</p>
        </footer>
    </div>
</body>
</html>"""
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
            