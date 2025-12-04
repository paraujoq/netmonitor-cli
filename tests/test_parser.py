"""
Tests unitarios para el parser de logs.
"""
from datetime import datetime
from pathlib import Path
import tempfile

import pytest

from netmonitor.parser import LogEntry, LogParser


class TestLogEntry:
    """Tests para el modelo LogEntry."""
    
    def test_valid_entry(self) -> None:
        """Test de creación de entrada válida."""
        entry = LogEntry(
            timestamp=datetime(2024, 10, 5, 14, 30, 0),
            level="ERROR",
            device="Router-01",
            message="Connection timeout",
        )
        
        assert entry.level == "ERROR"
        assert entry.device == "Router-01"
        assert entry.is_error is True
        assert entry.is_warning is False
    
    def test_level_normalization(self) -> None:
        """Test de normalización de nivel a mayúsculas."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level="error",  # minúsculas
            device="Test",
            message="Test message",
        )
        
        assert entry.level == "ERROR"  # debe convertirse a mayúsculas
    
    def test_invalid_level(self) -> None:
        """Test de validación de nivel inválido."""
        with pytest.raises(ValueError):
            LogEntry(
                timestamp=datetime.now(),
                level="INVALID",  # nivel no permitido
                device="Test",
                message="Test",
            )
    
    def test_warning_detection(self) -> None:
        """Test de detección de warnings."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level="WARNING",
            device="Test",
            message="Test warning",
        )
        
        assert entry.is_warning is True
        assert entry.is_error is False


class TestLogParser:
    """Tests para el LogParser."""
    
    def test_parse_valid_line(self) -> None:
        """Test de parseo de línea válida."""
        parser = LogParser(Path("dummy.log"))
        
        line = "2024-10-05 14:30:45 ERROR [Router-01] Connection timeout to 192.168.1.1"
        entry = parser._parse_line(line)
        
        assert entry.timestamp == datetime(2024, 10, 5, 14, 30, 45)
        assert entry.level == "ERROR"
        assert entry.device == "Router-01"
        assert "Connection timeout" in entry.message
    
    def test_parse_invalid_line(self) -> None:
        """Test de parseo de línea inválida."""
        parser = LogParser(Path("dummy.log"))
        
        line = "This is not a valid log line"
        
        with pytest.raises(ValueError):
            parser._parse_line(line)
    
    def test_parse_file(self) -> None:
        """Test de parseo de archivo completo."""
        # Crear archivo temporal con logs de prueba
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2024-10-05 10:00:00 INFO [Test-01] Test message 1\n")
            f.write("2024-10-05 10:01:00 ERROR [Test-02] Test error\n")
            f.write("# This is a comment\n")
            f.write("\n")  # línea vacía
            f.write("2024-10-05 10:02:00 WARNING [Test-01] Test warning\n")
            temp_path = Path(f.name)
        
        try:
            parser = LogParser(temp_path)
            entries = parser.parse()
            
            assert len(entries) == 3
            assert entries[0].level == "INFO"
            assert entries[1].level == "ERROR"
            assert entries[2].level == "WARNING"
        finally:
            temp_path.unlink()
    
    def test_error_tracking(self) -> None:
        """Test de tracking de errores de parseo."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            f.write("2024-10-05 10:00:00 INFO [Test] Valid line\n")
            f.write("Invalid line without proper format\n")
            f.write("2024-10-05 10:01:00 ERROR [Test] Another valid line\n")
            temp_path = Path(f.name)
        
        try:
            parser = LogParser(temp_path)
            entries = parser.parse()
            
            assert len(entries) == 2  # solo las líneas válidas
            assert parser.error_count == 1  # una línea con error
            
            errors = parser.get_errors()
            assert len(errors) == 1
            assert errors[0][0] == 2  # línea 2 tuvo error
        finally:
            temp_path.unlink()


# Para ejecutar los tests:
# pytest tests/test_parser.py -v
