from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QComboBox, QDateEdit, QLabel, QFileDialog,
                             QMessageBox)
from PyQt5.QtCore import Qt, QDate
from src.utils.report_manager import ReportManager
from src.gui.icons import icon_manager

class ReportWindow(QWidget):
    def __init__(self, report_manager: ReportManager, parent=None):
        super().__init__(parent)
        self.report_manager = report_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Rapor Oluştur")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Rapor tipi seçimi
        report_type_layout = QHBoxLayout()
        report_type_layout.addWidget(QLabel("Rapor Tipi:"))
        
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "Kullanıcı Aktivite Raporu",
            "Lisans Kullanım Raporu",
            "Şablon İstatistikleri"
        ])
        report_type_layout.addWidget(self.report_type_combo)
        
        layout.addLayout(report_type_layout)

        # Tarih aralığı seçimi
        date_range_layout = QHBoxLayout()
        date_range_layout.addWidget(QLabel("Başlangıç Tarihi:"))
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate().addDays(-30))
        date_range_layout.addWidget(self.start_date_edit)
        
        date_range_layout.addWidget(QLabel("Bitiş Tarihi:"))
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        date_range_layout.addWidget(self.end_date_edit)
        
        layout.addLayout(date_range_layout)

        # Çıktı formatı seçimi
        output_format_layout = QHBoxLayout()
        output_format_layout.addWidget(QLabel("Çıktı Formatı:"))
        
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(["PDF", "Excel", "CSV", "JSON"])
        output_format_layout.addWidget(self.output_format_combo)
        
        layout.addLayout(output_format_layout)

        # Butonlar
        button_layout = QHBoxLayout()
        
        generate_button = QPushButton("Rapor Oluştur")
        generate_button.clicked.connect(self.generate_report)
        icon_manager.set_icon(generate_button, "file")
        button_layout.addWidget(generate_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("Kapat")
        close_button.clicked.connect(self.close)
        icon_manager.set_icon(close_button, "quit")
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)

    def generate_report(self):
        """Rapor oluşturur"""
        report_type = self.report_type_combo.currentText()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
        output_format = self.output_format_combo.currentText().lower()
        
        try:
            if report_type == "Kullanıcı Aktivite Raporu":
                filepath = self.report_manager.generate_user_activity_report(
                    start_date, end_date, output_format
                )
            elif report_type == "Lisans Kullanım Raporu":
                filepath = self.report_manager.generate_license_usage_report(
                    start_date, end_date, output_format
                )
            else:  # Şablon İstatistikleri
                filepath = self.report_manager.generate_template_statistics(
                    start_date, end_date, output_format
                )
            
            QMessageBox.information(
                self,
                "Başarılı",
                f"Rapor başarıyla oluşturuldu:\n{filepath}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Rapor oluşturulurken hata oluştu: {str(e)}"
            ) 