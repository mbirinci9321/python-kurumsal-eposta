from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QFormLayout, QMessageBox,
    QTextEdit, QDialog, QDialogButtonBox, QDateEdit,
    QToolBar, QFileDialog, QHeaderView, QMenu, QGroupBox,
    QCheckBox, QSpinBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QDate
from utils.data_manager import DataManager
import csv
import json
from datetime import datetime, timedelta
from utils.license_manager import LicenseManager
from utils.auth_manager import AuthManager

class LicenseDialog(QDialog):
    """Lisans ekleme/düzenleme dialogu."""
    
    def __init__(self, parent, data_manager, license=None):
        super().__init__(parent)
        self.parent = parent
        self.data_manager = data_manager
        self.license = license
        
        self.setWindowTitle("Yeni Lisans" if license is None else "Lisans Düzenle")
        self.setMinimumWidth(400)
        
        # Ana layout
        layout = QVBoxLayout(self)
        
        # Form alanları
        form_layout = QFormLayout()
        
        # Kullanıcı
        self.user_combo = QComboBox()
        users = self.data_manager.get_users()
        for user in users:
            self.user_combo.addItem(user.get("name", ""), user.get("id", ""))
        if license:
            index = self.user_combo.findData(license["user_id"])
            if index >= 0:
                self.user_combo.setCurrentIndex(index)
        form_layout.addRow("Kullanıcı:", self.user_combo)
        
        # Lisans anahtarı
        self.key_input = QLineEdit()
        if license:
            self.key_input.setText(license["key"])
            self.key_input.setEnabled(False)  # Mevcut lisans anahtarı değiştirilemez
        form_layout.addRow("Lisans Anahtarı:", self.key_input)
        
        # Tür
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.data_manager.get_license_types())
        if license:
            index = self.type_combo.findText(license["type"])
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        form_layout.addRow("Tür:", self.type_combo)
        
        # Başlangıç tarihi
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        if license:
            self.start_date_edit.setDate(QDate.fromString(license["start_date"], "yyyy-MM-dd"))
        form_layout.addRow("Başlangıç:", self.start_date_edit)
        
        # Bitiş tarihi
        self.expiry_input = QDateEdit()
        self.expiry_input.setCalendarPopup(True)
        self.expiry_input.setDate(QDate.currentDate().addYears(1))
        if license:
            self.expiry_input.setDate(QDate.fromString(license["end_date"], "yyyy-MM-dd"))
        form_layout.addRow("Bitiş:", self.expiry_input)
        
        # Durum
        self.status_combo = QComboBox()
        self.status_combo.addItems(self.data_manager.get_license_statuses())
        if license:
            index = self.status_combo.findText(license["status"])
            if index >= 0:
                self.status_combo.setCurrentIndex(index)
        form_layout.addRow("Durum:", self.status_combo)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def accept(self):
        """Dialog verilerini kontrol eder ve kaydeder."""
        key = self.key_input.text().strip()
        type = self.type_combo.currentText()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.expiry_input.date().toString("yyyy-MM-dd")
        user_id = self.user_combo.currentData()
        status = self.status_combo.currentText()
        
        # Alanları kontrol et
        if not key:
            QMessageBox.warning(self, "Uyarı", "Lütfen lisans anahtarı girin.")
            return
        
        if not self.license and self.data_manager.get_license_by_key(key):
            QMessageBox.warning(self, "Uyarı", "Bu lisans anahtarı zaten kullanılıyor.")
            return
        
        try:
            license_data = {
                "key": key,
                "type": type,
                "start_date": start_date,
                "end_date": end_date,
                "user_id": user_id,
                "status": status
            }
            
            if self.license is None:
                # Yeni lisans ekle
                if not self.data_manager.add_license(license_data):
                    QMessageBox.critical(self, "Hata", "Lisans eklenirken bir hata oluştu.")
                    return
            else:
                # Mevcut lisansı güncelle
                if not self.data_manager.update_license(key, license_data):
                    QMessageBox.critical(self, "Hata", "Lisans güncellenirken bir hata oluştu.")
                    return
            
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

    def get_license_data(self):
        """Dialog verilerini döndürür."""
        return {
            'user_id': self.user_combo.currentData(),
            'key': self.key_input.text(),
            'expiry_date': self.expiry_input.date().toString(Qt.DateFormat.ISODate)
        }

class LicenseStatisticsDialog(QDialog):
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("Lisans İstatistikleri")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # İstatistik grupları
        stats = self.data_manager.get_license_statistics()
        
        # Genel istatistikler
        general_group = QGroupBox("Genel İstatistikler")
        general_layout = QFormLayout()
        general_layout.addRow("Toplam Lisans:", QLabel(str(stats["total"])))
        general_layout.addRow("Aktif Lisans:", QLabel(str(stats["active"])))
        general_layout.addRow("Süresi Dolmuş:", QLabel(str(stats["expired"])))
        general_layout.addRow("Askıya Alınmış:", QLabel(str(stats["suspended"])))
        general_layout.addRow("Son 30 Gün İçinde Eklenen:", QLabel(str(stats["new_licenses_30d"])))
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # Lisans türü dağılımı
        type_group = QGroupBox("Lisans Türü Dağılımı")
        type_layout = QFormLayout()
        for type_name, count in stats["type_distribution"].items():
            type_layout.addRow(f"{type_name}:", QLabel(str(count)))
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Yakında süresi dolacak lisanslar
        if stats["soon_to_expire"]:
            expiring_group = QGroupBox("Yakında Süresi Dolacak Lisanslar")
            expiring_layout = QFormLayout()
            for license in stats["soon_to_expire"]:
                user = self.data_manager.get_user_by_id(license["user_id"])
                user_name = user["full_name"] if user else "Bilinmeyen Kullanıcı"
                expiring_layout.addRow(
                    f"{license['key']} ({user_name}):",
                    QLabel(f"{license['days_left']} gün kaldı")
                )
            expiring_group.setLayout(expiring_layout)
            layout.addWidget(expiring_group)
        
        # Kapat butonu
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)

class BulkLicenseDialog(QDialog):
    def __init__(self, parent=None, data_manager=None, selected_licenses=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.selected_licenses = selected_licenses or []
        self.setWindowTitle("Toplu Lisans İşlemi")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Seçili lisans sayısı
        layout.addWidget(QLabel(f"Seçili Lisans Sayısı: {len(self.selected_licenses)}"))
        
        # İşlem seçenekleri
        form_layout = QFormLayout()
        
        # Durum güncelleme
        self.status_combo = QComboBox()
        self.status_combo.addItems(["ACTIVE", "SUSPENDED", "EXPIRED"])
        form_layout.addRow("Yeni Durum:", self.status_combo)
        
        # Süre uzatma
        self.extend_spin = QSpinBox()
        self.extend_spin.setRange(1, 365)
        self.extend_spin.setValue(30)
        form_layout.addRow("Süre Uzatma (Gün):", self.extend_spin)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)

    def accept(self):
        """Toplu güncelleme işlemini gerçekleştirir."""
        try:
            # Durum güncellemesi
            new_status = self.status_combo.currentText()
            
            # Süre uzatma
            days_to_extend = self.extend_spin.value()
            
            # Güncelleme verilerini hazırla
            update_data = {
                "status": new_status,
                "updated_at": datetime.now().isoformat()
            }
            
            # Lisansları güncelle
            updated = self.data_manager.bulk_update_licenses(self.selected_licenses, update_data)
            
            if updated > 0:
                QMessageBox.information(
                    self,
                    "Başarılı",
                    f"{updated} lisans başarıyla güncellendi."
                )
                super().accept()
            else:
                QMessageBox.warning(
                    self,
                    "Uyarı",
                    "Hiçbir lisans güncellenemedi."
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Lisanslar güncellenirken bir hata oluştu: {str(e)}"
            )

class LicenseWindow(QMainWindow):
    """Lisans yönetimi penceresi."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get managers from parent
        main_window = self.parent()
        if main_window:
            if hasattr(main_window, 'license_manager'):
                self.license_manager = main_window.license_manager
            if hasattr(main_window, 'auth_manager'):
                self.auth_manager = main_window.auth_manager
            if hasattr(main_window, 'data_manager'):
                self.data_manager = main_window.data_manager
        
        # If managers not found in parent, create new instances
        if not hasattr(self, 'license_manager'):
            from src.utils.license_manager import LicenseManager
            self.license_manager = LicenseManager()
        if not hasattr(self, 'auth_manager'):
            from src.utils.auth_manager import AuthManager
            self.auth_manager = AuthManager()
        if not hasattr(self, 'data_manager'):
            from src.utils.data_manager import DataManager
            self.data_manager = DataManager()
        
        self.setWindowTitle("Lisans Yönetimi")
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        self.main_layout = QVBoxLayout(central_widget)
        
        self.setup_ui()
        self.load_licenses()  # Initialize with licenses
        
    def setup_ui(self):
        # Üst toolbar
        toolbar = QHBoxLayout()
        
        self.add_button = QPushButton("Yeni Lisans")
        self.add_button.clicked.connect(self.show_add_dialog)
        toolbar.addWidget(self.add_button)
        
        self.renew_button = QPushButton("Yenile")
        self.renew_button.clicked.connect(self.renew_license)
        toolbar.addWidget(self.renew_button)
        
        self.deactivate_button = QPushButton("Devre Dışı Bırak")
        self.deactivate_button.clicked.connect(self.deactivate_license)
        toolbar.addWidget(self.deactivate_button)
        
        self.main_layout.addLayout(toolbar)
        
        # Lisans tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Kullanıcı ID", "Oluşturulma Tarihi",
            "Bitiş Tarihi", "Özellikler", "Durum"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        self.main_layout.addWidget(self.table)
        
        # Lisansları yükle
        self.load_licenses()
        
    def load_licenses(self):
        """Lisansları tabloya yükler."""
        licenses = self.license_manager.get_all_licenses()
        self.table.setRowCount(len(licenses))
        
        for row, (license_id, license_data) in enumerate(licenses.items()):
            self.table.setItem(row, 0, QTableWidgetItem(license_id))
            self.table.setItem(row, 1, QTableWidgetItem(license_data["user_id"]))
            self.table.setItem(row, 2, QTableWidgetItem(license_data["created_at"]))
            self.table.setItem(row, 3, QTableWidgetItem(license_data["expiry_date"]))
            self.table.setItem(row, 4, QTableWidgetItem(", ".join(license_data["features"])))
            self.table.setItem(row, 5, QTableWidgetItem("Aktif" if license_data["is_active"] else "Pasif"))
            
    def show_add_dialog(self):
        """Yeni lisans ekleme dialogunu gösterir."""
        dialog = LicenseDialog(self, self.data_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            license_data = dialog.get_license_data()
            if self.data_manager.add_license(license_data):
                self.load_licenses()
            else:
                QMessageBox.critical(self, "Hata", "Lisans eklenirken bir hata oluştu.")
    
    def show_edit_dialog(self):
        """Lisans düzenleme dialogunu gösterir."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek istediğiniz lisansı seçin.")
            return
            
        license_id = int(self.table.item(selected_row, 0).text())
        license_data = self.data_manager.get_license(license_id)
        
        if license_data:
            dialog = LicenseDialog(self, self.data_manager, license_data)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_data = dialog.get_license_data()
                if self.data_manager.update_license(license_id, updated_data):
                    self.load_licenses()
                else:
                    QMessageBox.critical(self, "Hata", "Lisans güncellenirken bir hata oluştu.")
                
    def renew_license(self):
        """Seçili lisansı yeniler."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen yenilemek istediğiniz lisansı seçin.")
            return
            
        license_id = self.table.item(selected_row, 0).text()
        
        dialog = LicenseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_license_data()
            success, message = self.license_manager.renew_license(
                license_id,
                data["duration_days"]
            )
            if success:
                QMessageBox.information(self, "Başarılı", message)
                self.load_licenses()
            else:
                QMessageBox.warning(self, "Hata", message)
                
    def deactivate_license(self):
        """Seçili lisansı devre dışı bırakır."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen devre dışı bırakmak istediğiniz lisansı seçin.")
            return
            
        license_id = self.table.item(selected_row, 0).text()
        license_user = self.table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Onay",
            f"{license_user} kullanıcısının lisansını devre dışı bırakmak istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.license_manager.deactivate_license(license_id)
            if success:
                QMessageBox.information(self, "Başarılı", message)
                self.load_licenses()
            else:
                QMessageBox.warning(self, "Hata", message)
                
    def show_context_menu(self, pos):
        """Bağlam menüsünü gösterir."""
        menu = QMenu()
        
        renew_action = menu.addAction("Yenile")
        renew_action.triggered.connect(self.renew_license)
        
        deactivate_action = menu.addAction("Devre Dışı Bırak")
        deactivate_action.triggered.connect(self.deactivate_license)
        
        menu.exec(self.table.viewport().mapToGlobal(pos)) 