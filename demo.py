"""
Script de demostración del NetMonitor CLI.
"""
from pathlib import Path
from netmonitor.parser import LogParser
from netmonitor.analyzer import LogAnalyzer
from netmonitor.reporter import Reporter


def main():
    """Ejecuta una demo completa del análisis de logs."""
    
    # 1. Parser
    print("\n🔍 Step 1: Parsing log file...")
    log_file = Path("sample_logs/network_demo.log")
    
    if not log_file.exists():
        print(f"❌ Error: Log file not found: {log_file}")
        return
    
    parser = LogParser(log_file)
    entries = parser.parse()
    
    print(f"✓ Parsed {len(entries)} log entries")
    if parser.error_count > 0:
        print(f"⚠ {parser.error_count} lines had parsing errors")
    
    # 2. Analyzer
    print("\n📊 Step 2: Analyzing logs...")
    analyzer = LogAnalyzer(entries)
    analysis = analyzer.analyze()
    
    print(f"✓ Analysis complete")
    print(f"  - Error rate: {analysis.error_rate:.1f}%")
    print(f"  - Duration: {analysis.duration_hours:.1f} hours")
    
    # 3. Reporter - Console
    print("\n📋 Step 3: Generating report...\n")
    reporter = Reporter(analysis)
    reporter.display_console()
    
    # 4. Export reports
    print("\n💾 Step 4: Exporting reports...")
    
    # Text report
    reporter.save(Path("output_report.txt"), format_type="text")
    
    # JSON report
    reporter.save(Path("output_report.json"), format_type="json")
    
    # HTML report
    reporter.save(Path("output_report.html"), format_type="html")
    
    print("\n✅ Demo complete!")
    print("\nGenerated files:")
    print("  - output_report.txt")
    print("  - output_report.json")
    print("  - output_report.html")
    print("\n💡 Open output_report.html in your browser to see the visual report!")


if __name__ == "__main__":
    main()