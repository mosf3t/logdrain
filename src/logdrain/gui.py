import sys
from pathlib import Path
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox, QProgressBar
)

from logdrain.ingestion.parser import PolyscopeLogParser
from logdrain.engine.drain_wrapper import DrainEngine
from logdrain.reporting.excel_exporter import ExcelReportGenerator
from logdrain.reporting.csv_exporter import CSVReportGenerator

class LogWorker(QThread):
    """Background worker thread to keep the GUI responsive during heavy parsing."""
    progress = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, log_path: str, output_path: str, output_format: str):
        super().__init__()
        self.log_path = log_path
        self.output_path = output_path
        self.output_format = output_format

    def run(self):
        try:
            self.progress.emit("Parsing log records...")
            parser = PolyscopeLogParser()
            records = parser.parse_file(self.log_path)
            
            self.progress.emit(f"Parsed {len(records)} records. Mining templates...")
            engine = DrainEngine()
            for rec in records:
                engine.process_message(rec.message_body)
            clusters = engine.get_cluster_stats()

            if self.output_format in ["excel", "both"]:
                self.progress.emit("Generating Excel diagnostic report...")
                exporter = ExcelReportGenerator(records, clusters)
                exporter.generate_workbook(self.output_path)

            if self.output_format in ["csv", "both"]:
                self.progress.emit("Generating CSV reports...")
                csv_exporter = CSVReportGenerator(records, clusters)
                csv_exporter.generate_csvs(self.output_path)

            self.finished.emit(f"Successfully generated reports for {len(records)} log entries!")
        except Exception as e:
            self.error.emit(str(e))


class DropZoneWidget(QLabel):
    """A user-friendly drag-and-drop target for support log files."""
    file_dropped = Signal(str)

    def __init__(self):
        super().__init__("Drag & Drop Polyscope Log File Here\n(or click 'Browse')")
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #1F4E78;
                border-radius: 8px;
                background-color: #F8F9FA;
                color: #333333;
                font-size: 14px;
                font-weight: bold;
                padding: 90px;
            }
            QLabel:hover {
                background-color: #E9ECEF;
            }
        """)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path:
                self.file_dropped.emit(file_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LogDrain - Polyscope Diagnostic Analyzer")
        self.setMinimumWidth(550)
        self.selected_file = None

        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Drop Zone
        self.drop_zone = DropZoneWidget()
        self.drop_zone.file_dropped.connect(self.set_file)
        layout.addWidget(self.drop_zone)

        # File Selection Info
        self.file_label = QLabel("No file selected.")
        self.file_label.setStyleSheet("color: #666666; font-style: italic;")
        layout.addWidget(self.file_label)

        # Controls Layout (Format selector & Browse button)
        controls_layout = QHBoxLayout()
        
        self.browse_btn = QPushButton("Browse Files...")
        self.browse_btn.clicked.connect(self.browse_file)
        controls_layout.addWidget(self.browse_btn)

        # Push the format selection to the right side of the row
        controls_layout.addStretch()

        # Tightly group format label and dropdown together with minimal spacing
        format_layout = QHBoxLayout()
        format_layout.setSpacing(6)
        format_layout.addWidget(QLabel("Format:"))


        self.format_combo = QComboBox()
        self.format_combo.addItems(["excel", "csv", "both"])
        format_layout.addWidget(self.format_combo)

        controls_layout.addLayout(format_layout)

        layout.addLayout(controls_layout)

        # Progress Bar & Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate spinner style while working
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Action Button
        self.analyze_btn = QPushButton("Generate Diagnostic Report")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #1F4E78;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)
        self.analyze_btn.setEnabled(False)
        self.analyze_btn.clicked.connect(self.run_analysis)
        layout.addWidget(self.analyze_btn)

    def set_file(self, file_path: str):
        self.selected_file = file_path
        self.file_label.setText(f"Selected: {Path(file_path).name}")
        self.file_label.setStyleSheet("color: #1F4E78; font-weight: bold;")
        self.analyze_btn.setEnabled(True)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Polyscope Log", "", "Log Files (*.log *.txt *.*);;All Files (*)")
        if file_path:
            self.set_file(file_path)

    def run_analysis(self):
        if not self.selected_file:
            return

        output_format = self.format_combo.currentText()
        default_ext = ".xlsx" if output_format in ["excel", "both"] else ".csv"
        
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Diagnostic Report", f"diagnostic_report{default_ext}")
        if not output_path:
            return

        self.analyze_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.progress_bar.show()

        # Start background worker
        self.worker = LogWorker(self.selected_file, output_path, output_format)
        self.worker.progress.connect(self.status_label.setText)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_analysis_error)
        self.worker.start()

    def on_analysis_finished(self, message: str):
        self.progress_bar.hide()
        self.status_label.setText(message)
        self.analyze_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        QMessageBox.information(self, "Success", message)

    def on_analysis_error(self, err_msg: str):
        self.progress_bar.hide()
        self.status_label.setText("Error occurred during processing.")
        self.analyze_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        QMessageBox.critical(self, "Analysis Error", f"An error occurred:\n{err_msg}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
