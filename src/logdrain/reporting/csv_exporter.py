import csv
from typing import List, Any, Dict

class CSVReportGenerator:
    """Exports parsed log records and cluster stats to flat CSV files."""

    def __init__(self, records: List[Any], clusters: List[Dict[str, Any]]):
        self.records = records
        self.clusters = clusters

    def generate_csvs(self, base_output_path: str) -> None:
        base_path = base_output_path.rsplit('.', 1)[0]
        logs_path = f"{base_path}_logs.csv"
        clusters_path = f"{base_path}_clusters.csv"

        # Export logs
        with open(logs_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Timestamp", "Severity", "Thread", "Logger Class", "Message Body", "Malformed"])
            for rec in self.records:
                writer.writerow([
                    rec.record_id,
                    str(rec.timestamp) if rec.timestamp else "N/A",
                    rec.severity,
                    rec.thread,
                    rec.logger_class,
                    rec.message_body,
                    rec.is_malformed
                ])

        # Export clusters
        with open(clusters_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Cluster ID", "Template Text", "Occurrence Count"])
            for cluster in self.clusters:
                writer.writerow([
                    cluster["cluster_id"],
                    cluster["template"],
                    cluster["size"]
                ])
