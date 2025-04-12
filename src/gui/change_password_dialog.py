from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDialogButtonBox, QMessageBox
)
from utils.auth_manager import AuthManager
from utils.logger import Logger

class ChangePasswordDialog(QDialog):
    """Şifre değiştirme dialogu."""
    
    def __init__(self, auth_manager: AuthManager, logger: Logger, parent=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.logger = logger
        
        self.setWindowTitle("Şifre Değiştir")
        self.setMinimumWidth(300)
        
        self.init_ui()
    
    def init_ui(self):
        """Dialog arayüzünü oluşturur."""
        layout = QVBoxLayout()
        
        # Form alanları
        form_layout = QFormLayout()
        
        self.current_password_edit = QLineEdit()
        self.current_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Mevcut Şifre:", self.current_password_edit)
        
        self.new_password_edit = QLineEdit()
        self.new_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Yeni Şifre:", self.new_password_edit)
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Yeni Şifre Tekrar:", self.confirm_password_edit)
        
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
        current_password = self.current_password_edit.text()
        new_password = self.new_password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        
        if not current_password or not new_password:
            QMessageBox.warning(self, "Uyarı", "Şifre alanları boş olamaz!")
            return
            
        if new_password != confirm_password:
            QMessageBox.warning(self, "Uyarı", "Yeni şifreler eşleşmiyor!")
            return
            
        if self.auth_manager.change_password(
            self.auth_manager.current_user_id,
            current_password,
            new_password
        ):
            self.logger.log_security("Şifre değiştirildi", self.auth_manager.current_user_id)
            QMessageBox.information(self, "Başarılı", "Şifreniz başarıyla değiştirildi!")
            super().accept()
        else:
            QMessageBox.critical(self, "Hata", "Mevcut şifre yanlış veya bir hata oluştu!") 