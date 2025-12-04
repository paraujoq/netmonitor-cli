"""
Analizador de logs con estadísticas y detección de patrones.
"""
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta

from netmonitor.parser import LogEntry


@dataclass
class LogAnalysis:
    """
    Resultados del análisis de logs.
    """
    total_entries: int
    date_range: tuple[datetime, datetime]
    level_distribution: dict[str, int]
    device_distribution: dict[str, int]
    top_errors: list[tuple[str, int]]
    errors_by_device: dict[str, int]
    hourly_distribution: dict[int, int]
    critical_events: list[LogEntry]
    
    @property
    def error_rate(self) -> float:
        """Calcula el porcentaje de errores."""
        errors = self.level_distribution.get("ERROR", 0)
        critical = self.level_distribution.get("CRITICAL", 0)
        return ((errors + critical) / self.total_entries * 100) if self.total_entries > 0 else 0.0
    
    @property
    def duration_hours(self) -> float:
        """Calcula la duración del período analizado en horas."""
        start, end = self.date_range
        return (end - start).total_seconds() / 3600


class LogAnalyzer:
    """
    Analiza patrones y genera estadísticas de logs.
    """
    
    def __init__(self, entries: list[LogEntry]) -> None:
        """
        Inicializa el analizador.
        
        Args:
            entries: Lista de entradas de log a analizar
        """
        self.entries = entries
    
    def analyze(self) -> LogAnalysis:
        """
        Ejecuta análisis completo de los logs.
        
        Returns:
            Objeto LogAnalysis con todos los resultados
        """
        if not self.entries:
            return self._empty_analysis()
        
        return LogAnalysis(
            total_entries=len(self.entries),
            date_range=self._calculate_date_range(),
            level_distribution=self._analyze_levels(),
            device_distribution=self._analyze_devices(),
            top_errors=self._find_top_errors(),
            errors_by_device=self._errors_by_device(),
            hourly_distribution=self._hourly_distribution(),
            critical_events=self._find_critical_events(),
        )
    
    def _empty_analysis(self) -> LogAnalysis:
        """Retorna un análisis vacío."""
        now = datetime.now()
        return LogAnalysis(
            total_entries=0,
            date_range=(now, now),
            level_distribution={},
            device_distribution={},
            top_errors=[],
            errors_by_device={},
            hourly_distribution={},
            critical_events=[],
        )
    
    def _calculate_date_range(self) -> tuple[datetime, datetime]:
        """Calcula el rango de fechas de los logs."""
        timestamps = [entry.timestamp for entry in self.entries]
        return (min(timestamps), max(timestamps))
    
    def _analyze_levels(self) -> dict[str, int]:
        """Cuenta la distribución de niveles de log."""
        counter = Counter(entry.level for entry in self.entries)
        return dict(counter)
    
    def _analyze_devices(self) -> dict[str, int]:
        """Cuenta eventos por dispositivo."""
        counter = Counter(entry.device for entry in self.entries)
        return dict(counter.most_common(10))  # Top 10 dispositivos
    
    def _find_top_errors(self, limit: int = 5) -> list[tuple[str, int]]:
        """
        Encuentra los mensajes de error más comunes.
        
        Args:
            limit: Número máximo de errores a retornar
            
        Returns:
            Lista de tuplas (mensaje, conteo)
        """
        error_entries = [
            entry for entry in self.entries 
            if entry.is_error
        ]
        
        # Simplificar mensajes (quitar IPs, números específicos)
        simplified_messages = [
            self._simplify_message(entry.message) 
            for entry in error_entries
        ]
        
        counter = Counter(simplified_messages)
        return counter.most_common(limit)
    
    def _simplify_message(self, message: str) -> str:
        """
        Simplifica un mensaje eliminando detalles variables.
        
        Reemplaza IPs, números, etc. para agrupar mensajes similares.
        """
        import re
        # Reemplazar IPs
        message = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', 'X.X.X.X', message)
        # Reemplazar números
        message = re.sub(r'\b\d+\b', 'N', message)
        return message
    
    def _errors_by_device(self) -> dict[str, int]:
        """Cuenta errores por dispositivo."""
        errors: defaultdict[str, int] = defaultdict(int)
        for entry in self.entries:
            if entry.is_error:
                errors[entry.device] += 1
        return dict(sorted(errors.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def _hourly_distribution(self) -> dict[int, int]:
        """Distribución de eventos por hora del día (0-23)."""
        hours: defaultdict[int, int] = defaultdict(int)
        for entry in self.entries:
            hours[entry.timestamp.hour] += 1
        return dict(sorted(hours.items()))
    
    def _find_critical_events(self) -> list[LogEntry]:
        """Retorna todos los eventos críticos."""
        return [
            entry for entry in self.entries 
            if entry.level == "CRITICAL"
        ]
    