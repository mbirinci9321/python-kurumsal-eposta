from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QFormLayout, QMessageBox,
    QTextEdit, QDialog, QDialogButtonBox, QDateEdit,
    QToolBar, QFileDialog, QHeaderView, QMenu
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QDate
from utils.data_manager import DataManager
import csv
import json

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
        
        # Anahtar
        self.key_edit = QLineEdit()
        if license:
            self.key_edit.setText(license["key"])
            self.key_edit.setEnabled(False)  # Mevcut lisans anahtarı değiştirilemez
        form_layout.addRow("Anahtar:", self.key_edit)
        
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
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate().addYears(1))
        if license:
            self.end_date_edit.setDate(QDate.fromString(license["end_date"], "yyyy-MM-dd"))
        form_layout.addRow("Bitiş:", self.end_date_edit)
        
        # Kullanıcı
        self.user_combo = QComboBox()
        users = self.data_manager.get_users()
        for user in users:
            self.user_combo.addItem(user["full_name"], user["id"])
        if license:
            index = self.user_combo.findData(license["user_id"])
            if index >= 0:
                self.user_combo.setCurrentIndex(index)
        form_layout.addRow("Kullanıcı:", self.user_combo)
        
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
        key = self.key_edit.text().strip()
        type = self.type_combo.currentText()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")
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

class LicenseWindow(QWidget):
    """Lisans yönetimi penceresi."""
    
    def __init__(self, data_manager, icon_manager):
        super().__init__()
        self.data_manager = data_manager
        self.icon_manager = icon_manager
        
        # Ana layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Araç çubuğunu oluştur
        self.create_toolbar()
        
        # Filtreleme alanını oluştur
        self.create_filter_area()
        
        # Lisans tablosunu oluştur
        self.create_license_table()
        
        # Alt araç çubuğunu oluştur
        self.create_bottom_toolbar()
        
        # Lisansları yükle
        self.load_licenses()
    
    def create_toolbar(self):
        """Araç çubuğunu oluşturur."""
        toolbar = QHBoxLayout()
        
        # Yeni lisans ekle butonu
        add_button = QPushButton("Ekle")
        add_button.clicked.connect(self.show_new_license_dialog)
        self.icon_manager.set_icon(add_button, "add")
        toolbar.addWidget(add_button)
        
        # Lisans düzenle butonu
        edit_button = QPushButton("Düzenle")
        edit_button.clicked.connect(self.show_edit_license_dialog)
        self.icon_manager.set_icon(edit_button, "edit")
        toolbar.addWidget(edit_button)
        
        # Lisans sil butonu
        delete_button = QPushButton("Sil")
        delete_button.clicked.connect(self.delete_license)
        self.icon_manager.set_icon(delete_button, "delete")
        toolbar.addWidget(delete_button)
        
        toolbar.addStretch()
        
        # Yenile butonu
        refresh_button = QPushButton("Yenile")
        refresh_button.clicked.connect(self.load_licenses)
        self.icon_manager.set_icon(refresh_button, "refresh")
        toolbar.addWidget(refresh_button)
        
        self.main_layout.addLayout(toolbar)
    
    def create_filter_area(self):
        """Filtre alanını oluştur"""
        filter_widget = QWidget()
        filter_layout = QHBoxLayout()
        
        # Lisans türü filtresi
        self.type_combo = QComboBox()
        self.type_combo.addItem("Tüm Türler", "")
        for license_type in self.data_manager.get_license_types():
            self.type_combo.addItem(license_type, license_type)
        self.type_combo.currentIndexChanged.connect(self.filter_licenses)
        filter_layout.addWidget(QLabel("Tür:"))
        filter_layout.addWidget(self.type_combo)
        
        # Durum filtresi
        self.status_combo = QComboBox()
        self.status_combo.addItem("Tüm Durumlar", "")
        for status in self.data_manager.get_license_statuses():
            self.status_combo.addItem(status, status)
        self.status_combo.currentIndexChanged.connect(self.filter_licenses)
        filter_layout.addWidget(QLabel("Durum:"))
        filter_layout.addWidget(self.status_combo)
        
        # Arama kutusu
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Lisans ara...")
        self.search_edit.textChanged.connect(self.filter_licenses)
        filter_layout.addWidget(QLabel("Ara:"))
        filter_layout.addWidget(self.search_edit)
        
        filter_widget.setLayout(filter_layout)
        self.main_layout.addWidget(filter_widget)
    
    def create_license_table(self):
        """Lisans tablosunu oluşturur."""
        self.license_table = QTableWidget()
        self.license_table.setColumnCount(6)
        self.license_table.setHorizontalHeaderLabels(["ID", "Lisans Anahtarı", "Tip", "Başlangıç", "Bitiş", "Durum"])
        self.license_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.license_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.license_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.license_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.license_table.customContextMenuRequested.connect(self.show_context_menu)
        self.license_table.setSortingEnabled(True)
        self.main_layout.addWidget(self.license_table)
    
    def create_bottom_toolbar(self):
        """Alt araç çubuğunu oluşturur."""
        bottom_toolbar = QToolBar()
        
        # Durum etiketi
        self.status_label = QLabel("Toplam 0 lisans")
        bottom_toolbar.addWidget(self.status_label)
        
        bottom_toolbar.addSeparator()
        
        # Yenile butonu
        refresh_action = QAction("Yenile", self)
        self.icon_manager.set_icon(refresh_action, "refresh")
        refresh_action.triggered.connect(self.load_licenses)
        bottom_toolbar.addAction(refresh_action)
        
        self.main_layout.addWidget(bottom_toolbar)
    
    def load_licenses(self):
        """Lisansları yükler ve tabloyu günceller."""
        # Lisans türü ve durum listelerini güncelle
        types = self.data_manager.get_license_types()
        self.type_combo.clear()
        self.type_combo.addItem("Tümü")
        self.type_combo.addItems(types)
        
        statuses = self.data_manager.get_license_statuses()
        self.status_combo.clear()
        self.status_combo.addItem("Tümü")
        self.status_combo.addItems(statuses)
        
        # Lisansları yükle
        licenses = self.data_manager.get_licenses()
        self.license_table.setRowCount(len(licenses))
        
        for row, license in enumerate(licenses):
            self.license_table.setItem(row, 0, QTableWidgetItem(str(license["id"])))
            self.license_table.setItem(row, 1, QTableWidgetItem(license["key"]))
            self.license_table.setItem(row, 2, QTableWidgetItem(license["type"]))
            self.license_table.setItem(row, 3, QTableWidgetItem(license["start_date"]))
            self.license_table.setItem(row, 4, QTableWidgetItem(license["end_date"]))
            self.license_table.setItem(row, 5, QTableWidgetItem(license["status"]))
        
        self.license_table.resizeColumnsToContents()
        self.status_label.setText(f"Toplam {len(licenses)} lisans")
    
    def filter_licenses(self):
        """Lisansları filtreler ve tabloya ekler."""
        type = self.type_combo.currentText()
        status = self.status_combo.currentText()
        search_text = self.search_edit.text().lower()
        
        # Tüm lisansları al
        licenses = self.data_manager.get_licenses()
        
        # Tür filtresi
        if type != "Tümü":
            licenses = [l for l in licenses if l["type"] == type]
        
        # Durum filtresi
        if status != "Tümü":
            licenses = [l for l in licenses if l["status"] == status]
        
        # Arama filtresi
        if search_text:
            licenses = [
                l for l in licenses
                if search_text in l["key"].lower() or
                search_text in str(l["user_id"]).lower()
            ]
        
        # Tabloyu güncelle
        self.license_table.setRowCount(len(licenses))
        for row, license in enumerate(licenses):
            self.license_table.setItem(row, 0, QTableWidgetItem(str(license["id"])))
            self.license_table.setItem(row, 1, QTableWidgetItem(license["key"]))
            self.license_table.setItem(row, 2, QTableWidgetItem(license["type"]))
            self.license_table.setItem(row, 3, QTableWidgetItem(license["start_date"]))
            self.license_table.setItem(row, 4, QTableWidgetItem(license["end_date"]))
            self.license_table.setItem(row, 5, QTableWidgetItem(license["status"]))
        
        # Sütun genişliklerini ayarla
        self.license_table.resizeColumnsToContents()
        
        # Durum etiketini güncelle
        self.status_label.setText(f"Toplam {len(licenses)} lisans")
    
    def show_new_license_dialog(self):
        """Yeni lisans ekleme penceresini gösterir."""
        dialog = LicenseDialog(self, self.data_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_licenses()
    
    def show_edit_license_dialog(self):
        """Lisans düzenleme dialogunu gösterir."""
        selected_items = self.license_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir lisans seçin.")
            return
        
        license_id = self.license_table.item(selected_items[0].row(), 0).text()
        license = self.data_manager.get_license_by_id(license_id)
        
        if license:
            dialog = LicenseDialog(self, self.data_manager, license)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_licenses()
    
    def delete_license(self):
        """Seçili lisansı siler."""
        selected_row = self.license_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek istediğiniz lisansı seçin.")
            return
        
        license_id = self.license_table.item(selected_row, 0).text()
        license = self.data_manager.get_license_by_id(license_id)
        
        reply = QMessageBox.question(
            self, "Onay",
            f"{license_id} lisansını silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.data_manager.delete_license(license_id)
                self.load_licenses()
                QMessageBox.information(self, "Başarılı", "Lisans başarıyla silindi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Lisans silinirken bir hata oluştu: {str(e)}")
    
    def show_context_menu(self, pos):
        """Bağlam menüsünü gösterir"""
        menu = QMenu()
        
        edit_action = QAction("Düzenle", self)
        edit_action.triggered.connect(self.show_edit_license_dialog)
        self.icon_manager.set_icon(edit_action, "edit")
        menu.addAction(edit_action)
        
        delete_action = QAction("Sil", self)
        delete_action.triggered.connect(self.delete_license)
        self.icon_manager.set_icon(delete_action, "delete")
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # Sütun gizleme/gösterme
        column_menu = menu.addMenu("Sütunlar")
        for i in range(self.license_table.columnCount()):
            action = QAction(self.license_table.horizontalHeaderItem(i).text(), self)
            action.setCheckable(True)
            action.setChecked(not self.license_table.isColumnHidden(i))
            action.triggered.connect(lambda checked, col=i: self.license_table.setColumnHidden(col, not checked))
            column_menu.addAction(action)
        
        menu.exec_(self.license_table.viewport().mapToGlobal(pos)) 