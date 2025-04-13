from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QLineEdit, QTableWidget, 
                            QTableWidgetItem, QMessageBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from ..utils.license_manager import LicenseManager

class LicenseWindow(QMainWindow):
    """Lisans yönetim penceresi."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.license_manager = LicenseManager()
        self.init_ui()
        
    def init_ui(self):
        """Arayüzü başlatır."""
        self.setWindowTitle("Lisans Yönetimi")
        self.setMinimumSize(800, 600)
        
        # Ana widget ve layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Üst panel - Lisans oluşturma
        top_panel = QWidget()
        top_layout = QHBoxLayout(top_panel)
        
        # Kullanıcı ID girişi
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Kullanıcı ID")
        top_layout.addWidget(QLabel("Kullanıcı ID:"))
        top_layout.addWidget(self.user_id_input)
        
        # Süre seçimi
        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("Süre (gün)")
        top_layout.addWidget(QLabel("Süre (gün):"))
        top_layout.addWidget(self.duration_input)
        
        # Lisans oluştur butonu
        create_btn = QPushButton("Lisans Oluştur")
        create_btn.clicked.connect(self.create_license)
        top_layout.addWidget(create_btn)
        
        layout.addWidget(top_panel)
        
        # Orta panel - Lisans listesi
        self.license_table = QTableWidget()
        self.license_table.setColumnCount(6)
        self.license_table.setHorizontalHeaderLabels([
            "Lisans ID", "Kullanıcı ID", "Oluşturulma Tarihi", 
            "Bitiş Tarihi", "Durum", "İşlemler"
        ])
        layout.addWidget(self.license_table)
        
        # Alt panel - Lisans yenileme
        bottom_panel = QWidget()
        bottom_layout = QHBoxLayout(bottom_panel)
        
        self.license_id_input = QLineEdit()
        self.license_id_input.setPlaceholderText("Lisans ID")
        bottom_layout.addWidget(QLabel("Lisans ID:"))
        bottom_layout.addWidget(self.license_id_input)
        
        self.renew_duration_input = QLineEdit()
        self.renew_duration_input.setPlaceholderText("Yenileme Süresi (gün)")
        bottom_layout.addWidget(QLabel("Yenileme Süresi:"))
        bottom_layout.addWidget(self.renew_duration_input)
        
        renew_btn = QPushButton("Lisansı Yenile")
        renew_btn.clicked.connect(self.renew_license)
        bottom_layout.addWidget(renew_btn)
        
        deactivate_btn = QPushButton("Lisansı Devre Dışı Bırak")
        deactivate_btn.clicked.connect(self.deactivate_license)
        bottom_layout.addWidget(deactivate_btn)
        
        layout.addWidget(bottom_panel)
        
        # Lisansları yükle
        self.load_licenses()
        
    def load_licenses(self):
        """Lisansları tabloya yükler."""
        self.license_table.setRowCount(0)
        licenses = self.license_manager.get_all_licenses()
        
        for license_id, license_data in licenses.items():
            row = self.license_table.rowCount()
            self.license_table.insertRow(row)
            
            # Lisans bilgilerini ekle
            self.license_table.setItem(row, 0, QTableWidgetItem(license_id))
            self.license_table.setItem(row, 1, QTableWidgetItem(license_data["user_id"]))
            self.license_table.setItem(row, 2, QTableWidgetItem(license_data["created_at"]))
            self.license_table.setItem(row, 3, QTableWidgetItem(license_data["expiry_date"]))
            
            # Durum
            status = "Aktif" if license_data["is_active"] else "Pasif"
            self.license_table.setItem(row, 4, QTableWidgetItem(status))
            
            # İşlem butonları
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            validate_btn = QPushButton("Doğrula")
            validate_btn.clicked.connect(lambda checked, lid=license_id: self.validate_license(lid))
            actions_layout.addWidget(validate_btn)
            
            self.license_table.setCellWidget(row, 5, actions_widget)
            
        self.license_table.resizeColumnsToContents()
        
    def create_license(self):
        """Yeni lisans oluşturur."""
        user_id = self.user_id_input.text().strip()
        duration = self.duration_input.text().strip()
        
        if not user_id or not duration:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return
            
        try:
            duration_days = int(duration)
            if duration_days <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçerli bir süre girin.")
            return
            
        license_id = self.license_manager.create_license(user_id, duration_days)
        if license_id:
            QMessageBox.information(self, "Başarılı", f"Lisans oluşturuldu. ID: {license_id}")
            self.load_licenses()
            self.user_id_input.clear()
            self.duration_input.clear()
        else:
            QMessageBox.critical(self, "Hata", "Lisans oluşturulurken bir hata oluştu.")
            
    def validate_license(self, license_id):
        """Lisansı doğrular."""
        is_valid, message = self.license_manager.validate_license(license_id)
        QMessageBox.information(self, "Doğrulama Sonucu", message)
        
    def renew_license(self):
        """Lisansı yeniler."""
        license_id = self.license_id_input.text().strip()
        duration = self.renew_duration_input.text().strip()
        
        if not license_id or not duration:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return
            
        try:
            duration_days = int(duration)
            if duration_days <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçerli bir süre girin.")
            return
            
        success, message = self.license_manager.renew_license(license_id, duration_days)
        if success:
            QMessageBox.information(self, "Başarılı", message)
            self.load_licenses()
            self.license_id_input.clear()
            self.renew_duration_input.clear()
        else:
            QMessageBox.critical(self, "Hata", message)
            
    def deactivate_license(self):
        """Lisansı devre dışı bırakır."""
        license_id = self.license_id_input.text().strip()
        
        if not license_id:
            QMessageBox.warning(self, "Hata", "Lütfen lisans ID'sini girin.")
            return
            
        success, message = self.license_manager.deactivate_license(license_id)
        if success:
            QMessageBox.information(self, "Başarılı", message)
            self.load_licenses()
            self.license_id_input.clear()
        else:
            QMessageBox.critical(self, "Hata", message) 