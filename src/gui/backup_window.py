from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QFileDialog, QLabel, QSpinBox, QProgressBar, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from src.utils.data_manager import DataManager
import os
from datetime import datetime
from .icons import IconManager

class BackupWindow(QWidget):
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.icon_manager = IconManager()
        self.init_ui()

    def init_ui(self):
        """Arayüz bileşenlerini oluşturur ve yerleştirir."""
        self.setWindowTitle('Yedekleme')
        self.setMinimumSize(600, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #333333;
                font-size: 12px;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
            }
            QLabel {
                color: #424242;
                font-size: 13px;
            }
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QFrame#separator {
                background-color: #E0E0E0;
            }
        """)
        
        # Ana düzen
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Başlık
        title_label = QLabel('Veri Yedekleme')
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Ayırıcı çizgi
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)
        
        # Yedekleme seçenekleri
        options_layout = QVBoxLayout()
        options_layout.setSpacing(10)
        
        # Yedekleme konumu seçimi
        location_layout = QHBoxLayout()
        self.location_label = QLabel('Yedekleme Konumu:')
        self.location_path = QLabel('Seçilmedi')
        self.location_path.setStyleSheet('color: #757575; font-style: italic;')
        self.select_location_btn = QPushButton('Konum Seç')
        self.select_location_btn.setIcon(self.icon_manager.get_icon('folder'))
        self.select_location_btn.clicked.connect(self.select_backup_location)
        
        location_layout.addWidget(self.location_label)
        location_layout.addWidget(self.location_path, 1)
        location_layout.addWidget(self.select_location_btn)
        options_layout.addLayout(location_layout)
        
        # İlerleme çubuğu
        progress_layout = QVBoxLayout()
        self.progress_label = QLabel('İlerleme:')
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        options_layout.addLayout(progress_layout)
        
        main_layout.addLayout(options_layout)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_backup_btn = QPushButton('Yedeklemeyi Başlat')
        self.start_backup_btn.setIcon(self.icon_manager.get_icon('backup'))
        self.start_backup_btn.clicked.connect(self.start_backup)
        self.start_backup_btn.setEnabled(False)
        
        self.cancel_btn = QPushButton('İptal')
        self.cancel_btn.setIcon(self.icon_manager.get_icon('cancel'))
        self.cancel_btn.clicked.connect(self.close)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5252;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        
        button_layout.addStretch()
        button_layout.addWidget(self.start_backup_btn)
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

        # Yedek listesi
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(2)
        self.backup_table.setHorizontalHeaderLabels(["Yedek Adı", "Tarih"])
        self.backup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.backup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        main_layout.addWidget(self.backup_table)

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

    def select_backup_location(self):
        """Yedekleme konumu seçme dialog'unu gösterir."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Yedekleme Konumu Seç",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if directory:
            self.location_path.setText(directory)
            self.location_path.setStyleSheet('color: #2E7D32; font-style: normal;')
            self.start_backup_btn.setEnabled(True)
    
    def start_backup(self):
        """Yedekleme işlemini başlatır."""
        # TODO: Yedekleme işlemi burada gerçekleştirilecek
        self.progress_bar.setValue(0)
        self.start_backup_btn.setEnabled(False)
        self.select_location_btn.setEnabled(False)
        
        # Simüle edilmiş yedekleme işlemi
        import time
        for i in range(101):
            time.sleep(0.05)
            self.progress_bar.setValue(i)
            if i == 100:
                QMessageBox.information(
                    self,
                    "Yedekleme Tamamlandı",
                    "Veriler başarıyla yedeklendi!",
                    QMessageBox.Ok
                )
                self.close()

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