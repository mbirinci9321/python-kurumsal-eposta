from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QFileDialog, QLabel, QSpinBox)
from PyQt5.QtCore import Qt
from src.utils.data_manager import DataManager
import os
from datetime import datetime

class BackupWindow(QWidget):
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Yedekleme Yönetimi")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)

        # Ana düzen
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Otomatik yedekleme ayarları
        backup_settings = QHBoxLayout()
        backup_settings.addWidget(QLabel("Otomatik Yedekleme Aralığı (saat):"))
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 168)  # 1 saat - 1 hafta
        self.interval_spin.setValue(24)
        self.interval_spin.valueChanged.connect(self.on_interval_changed)
        backup_settings.addWidget(self.interval_spin)
        
        backup_settings.addStretch()
        layout.addLayout(backup_settings)

        # Yedek listesi
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(2)
        self.backup_table.setHorizontalHeaderLabels(["Yedek Adı", "Tarih"])
        self.backup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.backup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout.addWidget(self.backup_table)

        # Butonlar
        button_layout = QHBoxLayout()
        
        self.backup_button = QPushButton("Yeni Yedek Oluştur")
        self.backup_button.clicked.connect(self.create_backup)
        button_layout.addWidget(self.backup_button)
        
        self.restore_button = QPushButton("Geri Yükle")
        self.restore_button.clicked.connect(self.restore_backup)
        button_layout.addWidget(self.restore_button)
        
        self.delete_button = QPushButton("Yedeği Sil")
        self.delete_button.clicked.connect(self.delete_backup)
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)

        # Yedekleri yükle
        self.load_backups()

    def load_backups(self):
        """Yedek listesini yükler"""
        self.backup_table.setRowCount(0)
        backups = self.data_manager.get_backups()
        
        for backup in backups:
            row = self.backup_table.rowCount()
            self.backup_table.insertRow(row)
            
            # Yedek adı
            self.backup_table.setItem(row, 0, QTableWidgetItem(backup))
            
            # Tarih
            try:
                date_str = backup.split("_")[1]
                date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                self.backup_table.setItem(row, 1, QTableWidgetItem(date.strftime("%d.%m.%Y %H:%M:%S")))
            except:
                self.backup_table.setItem(row, 1, QTableWidgetItem("Bilinmeyen"))

    def create_backup(self):
        """Yeni yedek oluşturur"""
        if self.data_manager.backup_data():
            QMessageBox.information(self, "Başarılı", "Yedekleme başarıyla tamamlandı.")
            self.load_backups()
        else:
            QMessageBox.critical(self, "Hata", "Yedekleme sırasında bir hata oluştu.")

    def restore_backup(self):
        """Seçili yedeği geri yükler"""
        selected = self.backup_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Uyarı", "Lütfen geri yüklenecek yedeği seçin.")
            return

        row = selected[0].row()
        backup_name = self.backup_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self,
            "Onay",
            f"{backup_name} yedeğini geri yüklemek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            backup_path = os.path.join(self.data_manager.data_dir, "backups", backup_name)
            if self.data_manager.restore_data(backup_path):
                QMessageBox.information(self, "Başarılı", "Geri yükleme başarıyla tamamlandı.")
            else:
                QMessageBox.critical(self, "Hata", "Geri yükleme sırasında bir hata oluştu.")

    def delete_backup(self):
        """Seçili yedeği siler"""
        selected = self.backup_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek yedeği seçin.")
            return

        row = selected[0].row()
        backup_name = self.backup_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self,
            "Onay",
            f"{backup_name} yedeğini silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            backup_path = os.path.join(self.data_manager.data_dir, "backups", backup_name)
            try:
                import shutil
                shutil.rmtree(backup_path)
                self.load_backups()
                QMessageBox.information(self, "Başarılı", "Yedek başarıyla silindi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Yedek silinirken bir hata oluştu: {str(e)}")

    def on_interval_changed(self, value):
        """Yedekleme aralığını günceller"""
        self.data_manager.set_backup_interval(value) 