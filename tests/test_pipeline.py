import pytest
from logdrain.ingestion.parser import PolyscopeLogParser
from logdrain.engine.drain_wrapper import DrainEngine

SAMPLE_LOG_DATA = """
2026-02-07 11:22:33.448 INFO Flight reporter triggered, safety mode: PROTECTIVE_STOP {thread: "AWT-EventQueue-0", loggerClass: com.ur.polyscope.flightrecorder.internal.reporter.FileSystemReporter}
2026-02-07 11:22:35.112 WARNING ControllerSocket[program="pause program "] {thread: "worker-1", loggerClass: com.ur.polyscope.controller.ControllerSocket}
026-02-07 11:22:38.445 INFO System recovered {thread: "main", loggerClass: com.ur.polyscope.System}
"""

def test_log_parser_framing_and_malformed_handling():
    parser = PolyscopeLogParser()
    records = parser.parse_string(SAMPLE_LOG_DATA.strip())
    
    assert len(records) == 3
    
    # Check normal record
    assert records[0].severity == "INFO"
    assert "PROTECTIVE_STOP" in records[0].message_body
    assert records[0].thread == "AWT-EventQueue-0"
    assert not records[0].is_malformed
    assert records[0].timestamp.year == 2026

    # Check multiline command body preservation
    assert "pause program" in records[1].message_body

    # Check malformed timestamp year correction (026- -> 2026-)
    assert records[2].timestamp.year == 2026
    assert records[2].is_malformed is False  # Corrected gracefully

def test_drain_engine_integration():
    parser = PolyscopeLogParser()
    engine = DrainEngine()
    
    records = parser.parse_string(SAMPLE_LOG_DATA.strip())
    
    mining_results = []
    for rec in records:
        res = engine.process_message(rec.message_body)
        mining_results.append(res)
        
    assert len(mining_results) == 3
    # Check that clusters were successfully generated
    clusters = engine.get_cluster_stats()
    assert len(clusters) > 0

def test_parameter_extractor():
    from logdrain.engine.parameter_extractor import ParameterExtractor
    extractor = ParameterExtractor()
    
    p1 = extractor.classify_parameter("/root/flightreports/recording20260206.zip")
    assert p1.category == "FILE_PATH"

    p2 = extractor.classify_parameter("PLAYING")
    assert p2.category == "STATE_OR_MODE"

    p3 = extractor.classify_parameter("1000")
    assert p3.category == "NUMERIC"

def test_excel_report_generation(tmp_path):
    from logdrain.ingestion.parser import PolyscopeLogParser
    from logdrain.engine.drain_wrapper import DrainEngine
    from logdrain.reporting.excel_exporter import ExcelReportGenerator

    parser = PolyscopeLogParser()
    engine = DrainEngine()
    records = parser.parse_string(SAMPLE_LOG_DATA.strip())
    
    for rec in records:
        engine.process_message(rec.message_body)

    output_file = tmp_path / "diagnostic_report.xlsx"
    exporter = ExcelReportGenerator(records, engine.get_cluster_stats())
    exporter.generate_workbook(str(output_file))

    assert output_file.exists()
    assert output_file.stat().st_size > 0


