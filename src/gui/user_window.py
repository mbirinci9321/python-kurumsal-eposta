from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit,
    QFormLayout, QMessageBox, QDialog, QLabel, QDialogButtonBox,
    QToolBar, QFileDialog, QHeaderView, QMenu
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal
from utils.data_manager import DataManager
import csv
import json

class UserWindow(QWidget):
    def __init__(self, data_manager: DataManager, icon_manager):
        super().__init__()
        self.data_manager = data_manager
        self.icon_manager = icon_manager
        self.layout = QVBoxLayout(self)
        
        # Araç çubuğunu oluştur
        self.create_toolbar()
        
        # Filtreleme alanını oluştur
        self.create_filter_area()
        
        # Kullanıcı tablosunu oluştur
        self.create_user_table()
        
        # Alt araç çubuğunu oluştur
        self.create_bottom_toolbar()
        
        # Kullanıcıları yükle
        self.load_users()
    
    def create_toolbar(self):
        """Araç çubuğunu oluşturur."""
        toolbar = QToolBar()
        
        # Yeni kullanıcı ekle butonu
        add_action = QAction("Yeni Kullanıcı", self)
        self.icon_manager.set_icon(add_action, "user_add")
        add_action.triggered.connect(self.show_new_user_dialog)
        toolbar.addAction(add_action)
        
        # Kullanıcı düzenle butonu
        edit_action = QAction("Kullanıcı Düzenle", self)
        self.icon_manager.set_icon(edit_action, "user_edit")
        edit_action.triggered.connect(self.show_edit_user_dialog)
        toolbar.addAction(edit_action)
        
        # Kullanıcı sil butonu
        delete_action = QAction("Kullanıcı Sil", self)
        self.icon_manager.set_icon(delete_action, "user_delete")
        delete_action.triggered.connect(self.delete_user)
        toolbar.addAction(delete_action)
        
        toolbar.addSeparator()
        
        # Toplu işlem butonları
        bulk_activate_action = QAction("Seçili Kullanıcıları Aktifleştir", self)
        self.icon_manager.set_icon(bulk_activate_action, "bulk_activate")
        bulk_activate_action.triggered.connect(self.bulk_activate_users)
        toolbar.addAction(bulk_activate_action)
        
        bulk_deactivate_action = QAction("Seçili Kullanıcıları Pasifleştir", self)
        self.icon_manager.set_icon(bulk_deactivate_action, "bulk_deactivate")
        bulk_deactivate_action.triggered.connect(self.bulk_deactivate_users)
        toolbar.addAction(bulk_deactivate_action)
        
        bulk_delete_action = QAction("Seçili Kullanıcıları Sil", self)
        self.icon_manager.set_icon(bulk_delete_action, "bulk_delete")
        bulk_delete_action.triggered.connect(self.bulk_delete_users)
        toolbar.addAction(bulk_delete_action)
        
        toolbar.addSeparator()
        
        # Dışa aktarma butonu
        export_action = QAction("Dışa Aktar", self)
        self.icon_manager.set_icon(export_action, "export")
        export_action.triggered.connect(self.export_users)
        toolbar.addAction(export_action)
        
        # İçe aktarma butonu
        import_action = QAction("İçe Aktar", self)
        self.icon_manager.set_icon(import_action, "import")
        import_action.triggered.connect(self.import_users)
        toolbar.addAction(import_action)
        
        self.layout.addWidget(toolbar)
    
    def create_filter_area(self):
        """Filtreleme alanını oluştur"""
        filter_widget = QWidget()
        filter_layout = QHBoxLayout()
        
        # Departman filtresi
        self.department_combo = QComboBox()
        self.department_combo.addItem("Tümü")
        for dept in self.data_manager.get_departments():
            self.department_combo.addItem(dept)
        self.department_combo.currentIndexChanged.connect(self.filter_users)
        filter_layout.addWidget(QLabel("Departman:"))
        filter_layout.addWidget(self.department_combo)
        
        # Rol filtresi
        self.role_combo = QComboBox()
        self.role_combo.addItem("Tümü")
        for role in self.data_manager.get_roles():
            self.role_combo.addItem(role)
        self.role_combo.currentIndexChanged.connect(self.filter_users)
        filter_layout.addWidget(QLabel("Rol:"))
        filter_layout.addWidget(self.role_combo)
        
        # Durum filtresi
        self.status_combo = QComboBox()
        self.status_combo.addItem("Tümü")
        self.status_combo.addItems(["Aktif", "Pasif"])
        self.status_combo.currentIndexChanged.connect(self.filter_users)
        filter_layout.addWidget(QLabel("Durum:"))
        filter_layout.addWidget(self.status_combo)
        
        # Arama kutusu
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Kullanıcı ara...")
        self.search_edit.textChanged.connect(self.filter_users)
        filter_layout.addWidget(QLabel("Ara:"))
        filter_layout.addWidget(self.search_edit)
        
        filter_widget.setLayout(filter_layout)
        self.layout.addWidget(filter_widget)
    
    def create_user_table(self):
        """Kullanıcı tablosunu oluşturur."""
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels([
            "ID", "Ad Soyad", "Departman", "Rol", "E-posta", "Durum"
        ])
        self.user_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.user_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.user_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.user_table.customContextMenuRequested.connect(self.show_context_menu)
        self.user_table.setSortingEnabled(True)
        self.layout.addWidget(self.user_table)
    
    def create_bottom_toolbar(self):
        """Alt araç çubuğunu oluşturur."""
        bottom_toolbar = QToolBar()
        
        # Durum etiketi
        self.status_label = QLabel("Toplam 0 kullanıcı")
        bottom_toolbar.addWidget(self.status_label)
        
        bottom_toolbar.addSeparator()
        
        # Yenile butonu
        refresh_action = QAction("Yenile", self)
        self.icon_manager.set_icon(refresh_action, "refresh")
        refresh_action.triggered.connect(self.load_users)
        bottom_toolbar.addAction(refresh_action)
        
        self.layout.addWidget(bottom_toolbar)
    
    def load_users(self):
        """Kullanıcıları yükler ve tabloyu günceller."""
        # Departman ve rol listelerini güncelle
        departments = self.data_manager.get_departments()
        self.department_combo.clear()
        self.department_combo.addItem("Tümü")
        self.department_combo.addItems(departments)
        
        roles = self.data_manager.get_roles()
        self.role_combo.clear()
        self.role_combo.addItem("Tümü")
        self.role_combo.addItems(roles)
        
        # Kullanıcıları yükle
        users = self.data_manager.get_users()
        self.user_table.setRowCount(len(users))
        
        for row, user in enumerate(users):
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user["id"])))
            self.user_table.setItem(row, 1, QTableWidgetItem(user.get("full_name", "")))
            self.user_table.setItem(row, 2, QTableWidgetItem(user.get("email", "")))
            self.user_table.setItem(row, 3, QTableWidgetItem(user.get("department", "")))
            self.user_table.setItem(row, 4, QTableWidgetItem(user.get("role", "")))
            self.user_table.setItem(row, 5, QTableWidgetItem(user.get("status", "")))
        
        self.user_table.resizeColumnsToContents()
        self.status_label.setText(f"Toplam {len(users)} kullanıcı")
    
    def filter_users(self):
        """Kullanıcıları filtreler ve tabloya ekler."""
        department = self.department_combo.currentText()
        role = self.role_combo.currentText()
        status = self.status_combo.currentText()
        search_text = self.search_edit.text().lower()
        
        # Tüm kullanıcıları al
        users = self.data_manager.get_users()
        
        # Departman filtresi
        if department != "Tümü":
            users = [u for u in users if u.get("department", "") == department]
        
        # Rol filtresi
        if role != "Tümü":
            users = [u for u in users if u.get("role", "") == role]
        
        # Durum filtresi
        if status != "Tümü":
            users = [u for u in users if u.get("status", "") == status]
        
        # Arama filtresi
        if search_text:
            users = [
                u for u in users
                if search_text in u.get("full_name", "").lower() or
                search_text in u.get("email", "").lower() or
                search_text in u.get("department", "").lower()
            ]
        
        # Tabloyu güncelle
        self.user_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user["id"])))
            self.user_table.setItem(row, 1, QTableWidgetItem(user.get("full_name", "")))
            self.user_table.setItem(row, 2, QTableWidgetItem(user.get("email", "")))
            self.user_table.setItem(row, 3, QTableWidgetItem(user.get("department", "")))
            self.user_table.setItem(row, 4, QTableWidgetItem(user.get("role", "")))
            self.user_table.setItem(row, 5, QTableWidgetItem(user.get("status", "")))
        
        # Sütun genişliklerini ayarla
        self.user_table.resizeColumnsToContents()
        
        # Durum etiketini güncelle
        self.status_label.setText(f"Toplam {len(users)} kullanıcı")
    
    def show_new_user_dialog(self):
        """Yeni kullanıcı ekleme penceresini gösterir."""
        dialog = UserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()
    
    def show_edit_user_dialog(self):
        """Kullanıcı düzenleme dialogunu gösterir."""
        selected_items = self.user_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir kullanıcı seçin.")
            return
        
        user_id = int(self.user_table.item(selected_items[0].row(), 0).text())
        user = self.data_manager.get_user_by_id(user_id)
        
        if user:
            dialog = UserDialog(self, user)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_users()
    
    def delete_user(self):
        """Seçili kullanıcıyı siler."""
        selected_row = self.user_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek istediğiniz kullanıcıyı seçin.")
            return
        
        user_id = int(self.user_table.item(selected_row, 0).text())
        user = self.data_manager.get_user_by_id(user_id)
        
        reply = QMessageBox.question(
            self, "Onay",
            f"{user['full_name']} kullanıcısını silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.data_manager.delete_user(user_id)
                self.load_users()
                QMessageBox.information(self, "Başarılı", "Kullanıcı başarıyla silindi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Kullanıcı silinirken bir hata oluştu: {str(e)}")
    
    def bulk_activate_users(self):
        """Seçili kullanıcıları aktifleştirir."""
        selected_rows = self.user_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir kullanıcı seçin.")
            return
            
        user_ids = set()
        for item in selected_rows:
            row = item.row()
            user_id = int(self.user_table.item(row, 0).text())
            user_ids.add(user_id)
            
        reply = QMessageBox.question(
            self,
            "Onay",
            f"{len(user_ids)} kullanıcı aktifleştirilecek. Devam etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for user_id in user_ids:
                self.data_manager.update_user(user_id, {"is_active": True})
            self.load_users()
            QMessageBox.information(self, "Bilgi", "Seçili kullanıcılar aktifleştirildi.")
            
    def bulk_deactivate_users(self):
        """Seçili kullanıcıları pasifleştirir."""
        selected_rows = self.user_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir kullanıcı seçin.")
            return
            
        user_ids = set()
        for item in selected_rows:
            row = item.row()
            user_id = int(self.user_table.item(row, 0).text())
            user_ids.add(user_id)
            
        reply = QMessageBox.question(
            self,
            "Onay",
            f"{len(user_ids)} kullanıcı pasifleştirilecek. Devam etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for user_id in user_ids:
                self.data_manager.update_user(user_id, {"is_active": False})
            self.load_users()
            QMessageBox.information(self, "Bilgi", "Seçili kullanıcılar pasifleştirildi.")
            
    def bulk_delete_users(self):
        """Seçili kullanıcıları siler."""
        selected_rows = self.user_table.selectedItems()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir kullanıcı seçin.")
            return
            
        user_ids = set()
        for item in selected_rows:
            row = item.row()
            user_id = int(self.user_table.item(row, 0).text())
            user_ids.add(user_id)
            
        reply = QMessageBox.question(
            self,
            "Onay",
            f"{len(user_ids)} kullanıcı silinecek. Bu işlem geri alınamaz. Devam etmek istiyor musunuz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            for user_id in user_ids:
                self.data_manager.delete_user(user_id)
            self.load_users()
            QMessageBox.information(self, "Bilgi", "Seçili kullanıcılar silindi.")
            
    def export_users(self):
        """Kullanıcıları dışa aktarır."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Kullanıcıları Dışa Aktar",
            "",
            "CSV Dosyaları (*.csv);;JSON Dosyaları (*.json)"
        )
        
        if file_path:
            users = self.data_manager.get_users()
            if file_path.endswith('.csv'):
                self._export_to_csv(users, file_path)
            else:
                self._export_to_json(users, file_path)
                
    def _export_to_csv(self, users, file_path):
        """Kullanıcıları CSV formatında dışa aktarır."""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Ad Soyad', 'E-posta', 'Departman', 'Rol', 'Durum'])
                for user in users:
                    writer.writerow([
                        user['id'],
                        user['full_name'],
                        user['email'],
                        user['department'],
                        user['role'],
                        'Aktif' if user['is_active'] else 'Pasif'
                    ])
            QMessageBox.information(self, "Bilgi", "Kullanıcılar başarıyla dışa aktarıldı.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dışa aktarma sırasında hata oluştu: {str(e)}")
            
    def _export_to_json(self, users, file_path):
        """Kullanıcıları JSON formatında dışa aktarır."""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "Bilgi", "Kullanıcılar başarıyla dışa aktarıldı.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dışa aktarma sırasında hata oluştu: {str(e)}")
            
    def import_users(self):
        """Kullanıcıları içe aktarır."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Kullanıcıları İçe Aktar",
            "",
            "CSV Dosyaları (*.csv);;JSON Dosyaları (*.json)"
        )
        
        if file_path:
            if file_path.endswith('.csv'):
                self._import_from_csv(file_path)
            else:
                self._import_from_json(file_path)
                
    def _import_from_csv(self, file_path):
        """CSV dosyasından kullanıcıları içe aktarır."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    user = {
                        'id': int(row['ID']),
                        'full_name': row['Ad Soyad'],
                        'email': row['E-posta'],
                        'department': row['Departman'],
                        'role': row['Rol'],
                        'is_active': row['Durum'] == 'Aktif'
                    }
                    self.data_manager.add_user(user)
            self.load_users()
            QMessageBox.information(self, "Bilgi", "Kullanıcılar başarıyla içe aktarıldı.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İçe aktarma sırasında hata oluştu: {str(e)}")
            
    def _import_from_json(self, file_path):
        """JSON dosyasından kullanıcıları içe aktarır."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                users = json.load(f)
                for user in users:
                    self.data_manager.add_user(user)
            self.load_users()
            QMessageBox.information(self, "Bilgi", "Kullanıcılar başarıyla içe aktarıldı.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İçe aktarma sırasında hata oluştu: {str(e)}")

    def show_context_menu(self, pos):
        """Bağlam menüsünü gösterir"""
        menu = QMenu()
        
        edit_action = QAction("Düzenle", self)
        edit_action.triggered.connect(self.show_edit_user_dialog)
        self.icon_manager.set_icon(edit_action, "edit")
        menu.addAction(edit_action)
        
        delete_action = QAction("Sil", self)
        delete_action.triggered.connect(self.delete_user)
        self.icon_manager.set_icon(delete_action, "delete")
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # Sütun gizleme/gösterme
        column_menu = menu.addMenu("Sütunlar")
        for i in range(self.user_table.columnCount()):
            action = QAction(self.user_table.horizontalHeaderItem(i).text(), self)
            action.setCheckable(True)
            action.setChecked(not self.user_table.isColumnHidden(i))
            action.triggered.connect(lambda checked, col=i: self.user_table.setColumnHidden(col, not checked))
            column_menu.addAction(action)
        
        menu.exec_(self.user_table.viewport().mapToGlobal(pos))

class UserDialog(QDialog):
    """Kullanıcı ekleme/düzenleme dialogu."""
    
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.data_manager = parent.data_manager
        
        self.setWindowTitle("Yeni Kullanıcı" if user is None else "Kullanıcı Düzenle")
        self.setMinimumWidth(400)
        
        # Ana layout
        layout = QVBoxLayout(self)
        
        # Form alanları
        form_layout = QFormLayout()
        
        # Ad Soyad
        self.name_edit = QLineEdit()
        if user:
            self.name_edit.setText(user["full_name"])
        form_layout.addRow("Ad Soyad:", self.name_edit)
        
        # E-posta
        self.email_edit = QLineEdit()
        if user:
            self.email_edit.setText(user["email"])
        form_layout.addRow("E-posta:", self.email_edit)
        
        # Departman
        self.department_combo = QComboBox()
        self.department_combo.addItem("Tümü")
        self.department_combo.addItems(self.data_manager.get_departments())
        if user:
            index = self.department_combo.findText(user["department"])
            if index >= 0:
                self.department_combo.setCurrentIndex(index)
        form_layout.addRow("Departman:", self.department_combo)
        
        # Rol
        self.role_combo = QComboBox()
        self.role_combo.addItems(self.data_manager.get_roles())
        if user:
            index = self.role_combo.findText(user["role"])
            if index >= 0:
                self.role_combo.setCurrentIndex(index)
        form_layout.addRow("Rol:", self.role_combo)
        
        # Durum
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Aktif", "Pasif"])
        if user:
            self.status_combo.setCurrentText("Aktif" if user["is_active"] else "Pasif")
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
        name = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        department = self.department_combo.currentText()
        role = self.role_combo.currentText()
        status = self.status_combo.currentText()
        
        # Alanları kontrol et
        if not name:
            QMessageBox.warning(self, "Uyarı", "Lütfen ad soyad girin.")
            return
        
        if not email:
            QMessageBox.warning(self, "Uyarı", "Lütfen e-posta girin.")
            return
        
        if department == "Tümü":
            QMessageBox.warning(self, "Uyarı", "Lütfen departman seçin.")
            return
        
        try:
            if self.user is None:
                # Yeni kullanıcı ekle
                self.data_manager.add_user({
                    "full_name": name,
                    "email": email,
                    "department": department,
                    "role": role,
                    "is_active": status == "Aktif"
                })
            else:
                # Mevcut kullanıcıyı güncelle
                self.data_manager.update_user(self.user["id"], {
                    "full_name": name,
                    "email": email,
                    "department": department,
                    "role": role,
                    "is_active": status == "Aktif"
                })
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e)) 