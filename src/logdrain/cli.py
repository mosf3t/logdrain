import argparse
import sys
from pathlib import Path
from logdrain.ingestion.parser import PolyscopeLogParser
from logdrain.engine.drain_wrapper import DrainEngine
from logdrain.reporting.excel_exporter import ExcelReportGenerator
from logdrain.reporting.csv_exporter import CSVReportGenerator

def main():
    parser = argparse.ArgumentParser(description="Analyze Universal Robots Polyscope support logs.")
    parser.add_argument("log_file", type=str, help="Path to the Polyscope support log file")
    parser.add_argument("-o", "--output", type=str, default="diagnostic_report.xlsx", help="Path to output report file")
    parser.add_argument("--format", choices=["excel", "csv", "both"], default="excel", help="Output report format")

    args = parser.parse_args()

    log_path = Path(args.log_file)
    if not log_path.exists():
        print(f"Error: Log file '{log_path}' not found.", file=sys.stderr)
        sys.exit(1)

    print(f"Parsing log file: {log_path}...")
    log_parser = PolyscopeLogParser()
    records = log_parser.parse_file(str(log_path))
    print(f"Parsed {len(records)} log records.")

    print("Running Drain3 template mining and parameter extraction...")
    engine = DrainEngine()
    for rec in records:
        engine.process_message(rec.message_body)

    clusters = engine.get_cluster_stats()

    if args.format in ["excel", "both"]:
        print(f"Generating Excel report: {args.output}...")
        exporter = ExcelReportGenerator(records, clusters)
        exporter.generate_workbook(args.output)

    if args.format in ["csv", "both"]:
        print(f"Generating CSV reports based on: {args.output}...")
        csv_exporter = CSVReportGenerator(records, clusters)
        csv_exporter.generate_csvs(args.output)

    print("Done! Diagnostic report(s) generated successfully.")

if __name__ == "__main__":
    main()
