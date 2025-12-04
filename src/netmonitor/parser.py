"""
Parser de logs de equipos de red con validación Pydantic.
"""
import re
from datetime import datetime
from pathlib import Path
from typing import Self
from typing import Literal

from pydantic import BaseModel, Field, field_validator
from loguru import logger


class LogEntry(BaseModel):
    """
    Representa una entrada de log validada.
    
    Ejemplo de formato esperado:
    2024-10-05 14:23:45 ERROR [Router-01] Connection timeout to 192.168.1.1
    """
    timestamp: datetime
    level: str = Field(pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    device: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=1)
    
    @field_validator("level", mode="before")
    @classmethod
    def level_uppercase(cls, v: str) -> str:
        """Normaliza el nivel a mayúsculas."""
        return v.upper()
    
    @property
    def is_error(self) -> bool:
        """Retorna True si es un error o crítico."""
        return self.level in ("ERROR", "CRITICAL")
    
    @property
    def is_warning(self) -> bool:
        """Retorna True si es warning."""
        return self.level == "WARNING"


class LogParser:
    """
    Parser de archivos de logs con soporte para múltiples formatos.
    """
    
    # Patrón regex para parsear logs
    # Formato: YYYY-MM-DD HH:MM:SS LEVEL [DEVICE] MESSAGE
    LOG_PATTERN = re.compile(
        r"^(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+"  # timestamp
        r"(\w+)\s+"                                      # level
        r"\[([^\]]+)\]\s+"                               # device
        r"(.+)$"                                         # message
    )
    
    def __init__(self, file_path: Path) -> None:
        """
        Inicializa el parser.
        
        Args:
            file_path: Ruta al archivo de logs
        """
        self.file_path = file_path
        self.entries: list[LogEntry] = []
        self._errors: list[tuple[int, str]] = []
    
    def parse(self) -> list[LogEntry]:
        """
        Parsea el archivo de logs completo.
        
        Returns:
            Lista de entradas de log validadas
        """
        logger.info(f"Iniciando parseo de: {self.file_path}")
        
        with open(self.file_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                try:
                    entry = self._parse_line(line)
                    self.entries.append(entry)
                except (ValueError, Exception) as e:
                    self._errors.append((line_num, str(e)))
                    logger.warning(f"Error en línea {line_num}: {e}")
        
        logger.info(
            f"Parseo completado: {len(self.entries)} entradas, "
            f"{len(self._errors)} errores"
        )
        
        return self.entries
    
    def _parse_line(self, line: str) -> LogEntry:
        """
        Parsea una línea individual del log.
        
        Args:
            line: Línea de texto del log
            
        Returns:
            LogEntry validado
            
        Raises:
            ValueError: Si la línea no coincide con el formato
        """
        match = self.LOG_PATTERN.match(line)
        if not match:
            raise ValueError(f"Formato inválido: {line[:50]}...")
        
        timestamp_str, level, device, message = match.groups()
        
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        
        return LogEntry(
            timestamp=timestamp,
            level=level,
            device=device,
            message=message,
        )
    
    @property
    def error_count(self) -> int:
        """Retorna el número de líneas con errores de parseo."""
        return len(self._errors)
    
    def get_errors(self) -> list[tuple[int, str]]:
        """Retorna lista de errores encontrados durante el parseo."""
        return self._errors.copy()
    