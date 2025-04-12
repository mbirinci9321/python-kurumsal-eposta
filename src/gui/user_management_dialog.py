from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox,
    QDialogButtonBox, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from utils.auth_manager import AuthManager
from utils.logger import Logger
from .icons import IconManager

class UserManagementDialog(QDialog):
    """Kullanıcı yönetimi dialogu."""
    
    def __init__(self, auth_manager: AuthManager, logger: Logger, parent=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.logger = logger
        self.icon_manager = IconManager()
        
        self.setWindowTitle("Kullanıcı Yönetimi")
        self.setMinimumSize(600, 400)
        
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        """Arayüzü oluşturur."""
        layout = QVBoxLayout()
        
        # Araç çubuğu
        toolbar = QHBoxLayout()
        
        add_button = QPushButton("Yeni Kullanıcı")
        add_button.clicked.connect(self.show_add_user_dialog)
        self.icon_manager.set_icon(add_button, "add")
        toolbar.addWidget(add_button)
        
        edit_button = QPushButton("Düzenle")
        edit_button.clicked.connect(self.show_edit_user_dialog)
        self.icon_manager.set_icon(edit_button, "edit")
        toolbar.addWidget(edit_button)
        
        delete_button = QPushButton("Sil")
        delete_button.clicked.connect(self.delete_user)
        self.icon_manager.set_icon(delete_button, "delete")
        toolbar.addWidget(delete_button)
        
        toolbar.addStretch()
        
        # Arama
        search_label = QLabel("Ara:")
        toolbar.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Kullanıcı ara...")
        self.search_edit.textChanged.connect(self.filter_users)
        toolbar.addWidget(self.search_edit)
        
        layout.addLayout(toolbar)
        
        # Kullanıcı tablosu
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels([
            "ID", "Kullanıcı Adı", "Rol", "Durum", "Son Güncelleme"
        ])
        header = self.user_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # ID column
        for i in range(1, 5):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.user_table)
        
        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Close
        )
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def load_users(self):
        """Kullanıcıları yükler."""
        users = self.auth_manager.get_all_users()
        self.user_table.setRowCount(len(users))
        
        for i, user in enumerate(users):
            self.user_table.setItem(i, 0, QTableWidgetItem(str(user["id"])))
            self.user_table.setItem(i, 1, QTableWidgetItem(user["username"]))
            self.user_table.setItem(i, 2, QTableWidgetItem(user["role"]))
            self.user_table.setItem(i, 3, QTableWidgetItem("Aktif" if user["is_active"] else "Pasif"))
            self.user_table.setItem(i, 4, QTableWidgetItem(user["updated_at"]))
    
    def filter_users(self):
        """Kullanıcıları filtreler."""
        search_text = self.search_edit.text().lower()
        
        for i in range(self.user_table.rowCount()):
            row_hidden = True
            for j in range(self.user_table.columnCount()):
                item = self.user_table.item(i, j)
                if item and search_text in item.text().lower():
                    row_hidden = False
                    break
            self.user_table.setRowHidden(i, row_hidden)
    
    def show_add_user_dialog(self):
        """Yeni kullanıcı ekleme dialogunu gösterir."""
        dialog = UserDialog(self.auth_manager, self.logger, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()
    
    def show_edit_user_dialog(self):
        """Kullanıcı düzenleme dialogunu gösterir."""
        current_row = self.user_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlenecek kullanıcıyı seçin!")
            return
            
        user_id = int(self.user_table.item(current_row, 0).text())
        user = self.auth_manager.get_user(user_id)
        
        if user:
            dialog = UserDialog(self.auth_manager, self.logger, user, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_users()
    
    def delete_user(self):
        """Seçili kullanıcıyı siler."""
        current_row = self.user_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek kullanıcıyı seçin!")
            return
            
        user_id = int(self.user_table.item(current_row, 0).text())
        
        reply = QMessageBox.question(
            self,
            "Kullanıcı Sil",
            "Bu kullanıcıyı silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.auth_manager.delete_user(user_id):
                self.logger.log_security("Kullanıcı silindi", user_id)
                self.load_users()
            else:
                QMessageBox.critical(self, "Hata", "Kullanıcı silinirken bir hata oluştu!")

class UserDialog(QDialog):
    """Kullanıcı ekleme/düzenleme dialogu."""
    
    def __init__(self, auth_manager: AuthManager, logger: Logger, user=None, parent=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.logger = logger
        self.user = user
        
        self.setWindowTitle("Kullanıcı Ekle" if not user else "Kullanıcı Düzenle")
        self.setMinimumWidth(400)
        
        self.init_ui()
    
    def init_ui(self):
        """Dialog arayüzünü oluşturur."""
        layout = QVBoxLayout()
        
        # Form alanları
        form_layout = QFormLayout()
        
        self.username_edit = QLineEdit()
        if self.user:
            self.username_edit.setText(self.user["username"])
            self.username_edit.setEnabled(False)
        form_layout.addRow("Kullanıcı Adı:", self.username_edit)
        
        if not self.user:
            self.password_edit = QLineEdit()
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            form_layout.addRow("Şifre:", self.password_edit)
            
            self.confirm_password_edit = QLineEdit()
            self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            form_layout.addRow("Şifre Tekrar:", self.confirm_password_edit)
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "manager", "admin"])
        if self.user:
            self.role_combo.setCurrentText(self.user["role"])
        form_layout.addRow("Rol:", self.role_combo)
        
        self.is_active_combo = QComboBox()
        self.is_active_combo.addItems(["Aktif", "Pasif"])
        if self.user:
            self.is_active_combo.setCurrentText("Aktif" if self.user["is_active"] else "Pasif")
        form_layout.addRow("Durum:", self.is_active_combo)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def accept(self):
        """Dialog kabul edildiğinde çalışır."""
        username = self.username_edit.text()
        role = self.role_combo.currentText()
        is_active = self.is_active_combo.currentText() == "Aktif"
        
        if not username:
            QMessageBox.warning(self, "Uyarı", "Kullanıcı adı boş olamaz!")
            return
            
        if not self.user:
            # Yeni kullanıcı
            password = self.password_edit.text()
            confirm_password = self.confirm_password_edit.text()
            
            if not password:
                QMessageBox.warning(self, "Uyarı", "Şifre boş olamaz!")
                return
                
            if password != confirm_password:
                QMessageBox.warning(self, "Uyarı", "Şifreler eşleşmiyor!")
                return
                
            if self.auth_manager.register(username, password, role):
                self.logger.log_security("Yeni kullanıcı oluşturuldu", username)
                super().accept()
            else:
                QMessageBox.critical(self, "Hata", "Kullanıcı oluşturulurken bir hata oluştu!")
        else:
            # Kullanıcı güncelleme
            user_data = {
                "role": role,
                "is_active": is_active
            }
            
            if self.auth_manager.update_user(self.user["id"], user_data):
                self.logger.log_security("Kullanıcı güncellendi", self.user["id"])
                super().accept()
            else:
                QMessageBox.critical(self, "Hata", "Kullanıcı güncellenirken bir hata oluştu!") 