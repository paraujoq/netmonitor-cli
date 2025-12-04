"""
Tests para el módulo analyzer.
"""
import pytest
from datetime import datetime, timedelta
from netmonitor.parser import LogEntry
from netmonitor.analyzer import LogAnalyzer, LogAnalysis


class TestLogAnalyzerBasics:
    """Tests básicos del analizador."""
    
    @pytest.fixture
    def sample_entries(self) -> list[LogEntry]:
        """Fixture con entradas de log de muestra."""
        base_time = datetime(2024, 12, 4, 8, 0, 0)
        return [
            LogEntry(
                timestamp=base_time,
                level="ERROR",
                device="Router-01",
                message="Connection timeout to 192.168.1.1",
            ),
            LogEntry(
                timestamp=base_time + timedelta(minutes=15),
                level="ERROR",
                device="Router-01",
                message="Connection timeout to 192.168.1.2",
            ),
            LogEntry(
                timestamp=base_time + timedelta(minutes=30),
                level="CRITICAL",
                device="Switch-02",
                message="Power failure detected",
            ),
            LogEntry(
                timestamp=base_time + timedelta(hours=1),
                level="WARNING",
                device="Switch-02",
                message="High CPU usage: 85%",
            ),
            LogEntry(
                timestamp=base_time + timedelta(hours=2),
                level="INFO",
                device="Router-01",
                message="Link up on port 24",
            ),
        ]
    
    def test_analyzer_initialization(self, sample_entries: list[LogEntry]) -> None:
        """Test que el analyzer se inicializa correctamente."""
        analyzer = LogAnalyzer(sample_entries)
        assert analyzer is not None
        assert len(analyzer.entries) == 5
    
    def test_analyze_returns_log_analysis(
        self, sample_entries: list[LogEntry]
    ) -> None:
        """Test que analyze() retorna un objeto LogAnalysis."""
        analyzer = LogAnalyzer(sample_entries)
        result = analyzer.analyze()
        
        assert isinstance(result, LogAnalysis)
        assert result.total_entries == 5
    
    def test_level_distribution(self, sample_entries: list[LogEntry]) -> None:
        """Test distribución de niveles de log."""
        analyzer = LogAnalyzer(sample_entries)
        result = analyzer.analyze()
        
        assert result.level_distribution["ERROR"] == 2
        assert result.level_distribution["CRITICAL"] == 1
        assert result.level_distribution["WARNING"] == 1
        assert result.level_distribution["INFO"] == 1
    
    def test_device_distribution(self, sample_entries: list[LogEntry]) -> None:
        """Test distribución por dispositivo."""
        analyzer = LogAnalyzer(sample_entries)
        result = analyzer.analyze()
        
        assert result.device_distribution["Router-01"] == 3
        assert result.device_distribution["Switch-02"] == 2
    
    def test_date_range(self, sample_entries: list[LogEntry]) -> None:
        """Test cálculo del rango de fechas."""
        analyzer = LogAnalyzer(sample_entries)
        result = analyzer.analyze()
        
        start, end = result.date_range
        assert start == datetime(2024, 12, 4, 8, 0, 0)
        assert end == datetime(2024, 12, 4, 10, 0, 0)
    
    def test_error_rate(self, sample_entries: list[LogEntry]) -> None:
        """Test cálculo de error rate."""
        analyzer = LogAnalyzer(sample_entries)
        result = analyzer.analyze()
        
        # 2 ERROR + 1 CRITICAL = 3 de 5 = 60%
        assert result.error_rate == 60.0
    
    def test_duration_hours(self, sample_entries: list[LogEntry]) -> None:
        """Test cálculo de duración en horas."""
        analyzer = LogAnalyzer(sample_entries)
        result = analyzer.analyze()
        
        # De 08:00 a 10:00 = 2 horas
        assert result.duration_hours == 2.0


class TestLogAnalyzerEdgeCases:
    """Tests de casos especiales."""
    
    def test_empty_entries(self) -> None:
        """Test con lista vacía de entradas."""
        analyzer = LogAnalyzer([])
        result = analyzer.analyze()
        
        assert result.total_entries == 0
        assert result.error_rate == 0.0
        assert result.level_distribution == {}
        assert result.device_distribution == {}
        assert result.top_errors == []
        assert result.errors_by_device == {}
        assert result.critical_events == []
    
    def test_only_errors(self) -> None:
        """Test con solo errores."""
        entries = [
            LogEntry(
                timestamp=datetime.now(),
                level="ERROR",
                device=f"Device-{i}",
                message="Error message",
            )
            for i in range(5)
        ]
        
        analyzer = LogAnalyzer(entries)
        result = analyzer.analyze()
        
        assert result.total_entries == 5
        assert result.error_rate == 100.0
        assert result.level_distribution["ERROR"] == 5
    
    def test_only_critical(self) -> None:
        """Test con solo eventos críticos."""
        entries = [
            LogEntry(
                timestamp=datetime.now(),
                level="CRITICAL",
                device="Device-01",
                message="Critical event",
            )
            for _ in range(3)
        ]
        
        analyzer = LogAnalyzer(entries)
        result = analyzer.analyze()
        
        assert result.total_entries == 3
        assert result.error_rate == 100.0
        assert len(result.critical_events) == 3
    
    def test_single_entry(self) -> None:
        """Test con una sola entrada."""
        entry = LogEntry(
            timestamp=datetime.now(),
            level="WARNING",
            device="Device-01",
            message="Test",
        )
        
        analyzer = LogAnalyzer([entry])
        result = analyzer.analyze()
        
        assert result.total_entries == 1
        assert result.level_distribution["WARNING"] == 1
        assert result.error_rate == 0.0


class TestLogAnalyzerErrorDetection:
    """Tests de detección de errores."""
    
    def test_errors_by_device(self) -> None:
        """Test conteo de errores por dispositivo."""
        entries = [
            LogEntry(
                timestamp=datetime.now(),
                level="ERROR",
                device="Router-01",
                message="Error 1",
            ),
            LogEntry(
                timestamp=datetime.now(),
                level="ERROR",
                device="Router-01",
                message="Error 2",
            ),
            LogEntry(
                timestamp=datetime.now(),
                level="CRITICAL",
                device="Switch-02",
                message="Critical",
            ),
            LogEntry(
                timestamp=datetime.now(),
                level="INFO",
                device="Router-01",
                message="Info",
            ),
        ]
        
        analyzer = LogAnalyzer(entries)
        result = analyzer.analyze()
        
        assert result.errors_by_device["Router-01"] == 2
        assert result.errors_by_device["Switch-02"] == 1
    
    def test_top_errors_grouping(self) -> None:
        """Test que top_errors agrupa mensajes similares."""
        entries = [
            LogEntry(
                timestamp=datetime.now(),
                level="ERROR",
                device="Router-01",
                message="Connection timeout to 192.168.1.1",
            ),
            LogEntry(
                timestamp=datetime.now(),
                level="ERROR",
                device="Router-02",
                message="Connection timeout to 192.168.1.2",
            ),
            LogEntry(
                timestamp=datetime.now(),
                level="ERROR",
                device="Router-03",
                message="Connection timeout to 10.0.0.1",
            ),
        ]
        
        analyzer = LogAnalyzer(entries)
        result = analyzer.analyze()
        
        # Los 3 errores deberían agruparse como el mismo
        assert len(result.top_errors) == 1
        assert result.top_errors[0][1] == 3  # 3 ocurrencias
        assert "X.X.X.X" in result.top_errors[0][0]  # IP simplificada
    
    def test_critical_events_filtering(self) -> None:
        """Test que critical_events solo retorna CRITICAL."""
        entries = [
            LogEntry(
                timestamp=datetime.now(),
                level="CRITICAL",
                device="Device-01",
                message="Critical 1",
            ),
            LogEntry(
                timestamp=datetime.now(),
                level="ERROR",
                device="Device-02",
                message="Error",
            ),
            LogEntry(
                timestamp=datetime.now(),
                level="CRITICAL",
                device="Device-03",
                message="Critical 2",
            ),
        ]
        
        analyzer = LogAnalyzer(entries)
        result = analyzer.analyze()
        
        assert len(result.critical_events) == 2
        assert all(e.level == "CRITICAL" for e in result.critical_events)


class TestLogAnalyzerTimeDistribution:
    """Tests de distribución temporal."""
    
    def test_hourly_distribution(self) -> None:
        """Test distribución por hora del día."""
        base = datetime(2024, 12, 4, 8, 0, 0)
        entries = [
            LogEntry(
                timestamp=base.replace(hour=8),
                level="INFO",
                device="Device-01",
                message="Morning 1",
            ),
            LogEntry(
                timestamp=base.replace(hour=8, minute=30),
                level="INFO",
                device="Device-01",
                message="Morning 2",
            ),
            LogEntry(
                timestamp=base.replace(hour=14),
                level="ERROR",
                device="Device-01",
                message="Afternoon",
            ),
            LogEntry(
                timestamp=base.replace(hour=20),
                level="INFO",
                device="Device-01",
                message="Evening",
            ),
        ]
        
        analyzer = LogAnalyzer(entries)
        result = analyzer.analyze()
        
        assert result.hourly_distribution[8] == 2
        assert result.hourly_distribution[14] == 1
        assert result.hourly_distribution[20] == 1


class TestLogAnalyzerPerformance:
    """Tests de performance con datasets grandes."""
    
    @pytest.mark.parametrize("num_entries", [100, 500, 1000])
    def test_large_datasets(self, num_entries: int) -> None:
        """Test con diferentes tamaños de datasets."""
        entries = [
            LogEntry(
                timestamp=datetime.now(),
                level="INFO",
                device="Device-01",
                message=f"Message {i}",
            )
            for i in range(num_entries)
        ]
        
        analyzer = LogAnalyzer(entries)
        result = analyzer.analyze()
        
        assert result.total_entries == num_entries
        assert result.error_rate == 0.0
    
    def test_many_devices(self) -> None:
        """Test con muchos dispositivos diferentes."""
        entries = [
            LogEntry(
                timestamp=datetime.now(),
                level="INFO",
                device=f"Device-{i:03d}",
                message="Test",
            )
            for i in range(100)
        ]
        
        analyzer = LogAnalyzer(entries)
        result = analyzer.analyze()
        
        # device_distribution retorna top 10
        assert len(result.device_distribution) == 10
        