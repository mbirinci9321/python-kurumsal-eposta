from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QLabel, QLineEdit, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon
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
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        self.load_users()
    
    def init_ui(self):
        """Kullanıcı yönetimi arayüzünü oluşturur."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #424242;
                font-size: 13px;
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
            QPushButton#deleteButton {
                background-color: #FF5252;
            }
            QPushButton#deleteButton:hover {
                background-color: #D32F2F;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                gridline-color: #F5F5F5;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #FAFAFA;
                color: #424242;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #E0E0E0;
            }
            QFrame#searchFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 10px;
            }
        """)

        # Ana düzen
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Başlık
        title_label = QLabel('Kullanıcı Yönetimi')
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Arama çerçevesi
        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_layout = QHBoxLayout(search_frame)
        
        search_label = QLabel('Kullanıcı Ara:')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Ad, soyad veya e-posta ile arama yapın...')
        self.search_input.textChanged.connect(self.filter_users)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addWidget(search_frame)

        # Kullanıcı tablosu
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels(['Ad', 'Soyad', 'E-posta', 'Grup'])
        
        header = self.user_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        
        layout.addWidget(self.user_table)

        # Buton çerçevesi
        button_frame = QFrame()
        button_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        button_layout = QHBoxLayout(button_frame)
        button_layout.setSpacing(10)

        # Kullanıcı işlem butonları
        self.add_button = QPushButton('Kullanıcı Ekle')
        self.add_button.setIcon(self.icon_manager.get_icon('add_user'))
        self.add_button.clicked.connect(self.show_add_user_dialog)

        self.edit_button = QPushButton('Düzenle')
        self.edit_button.setIcon(self.icon_manager.get_icon('edit'))
        self.edit_button.clicked.connect(self.show_edit_user_dialog)

        self.delete_button = QPushButton('Sil')
        self.delete_button.setObjectName("deleteButton")
        self.delete_button.setIcon(self.icon_manager.get_icon('delete'))
        self.delete_button.clicked.connect(self.delete_user)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addStretch()

        close_button = QPushButton('Kapat')
        close_button.setIcon(self.icon_manager.get_icon('cancel'))
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        layout.addWidget(button_frame)
        self.setLayout(layout)
    
    def load_users(self):
        """Kullanıcı listesini yükler."""
        self.user_table.setRowCount(0)
        users = self.auth_manager.get_users()
        
        for user in users:
            row = self.user_table.rowCount()
            self.user_table.insertRow(row)
            
            self.user_table.setItem(row, 0, QTableWidgetItem(user.get('first_name', '')))
            self.user_table.setItem(row, 1, QTableWidgetItem(user.get('last_name', '')))
            self.user_table.setItem(row, 2, QTableWidgetItem(user.get('email', '')))
            self.user_table.setItem(row, 3, QTableWidgetItem(user.get('group', '')))
    
    def filter_users(self):
        """Kullanıcıları arama metnine göre filtreler."""
        search_text = self.search_input.text().lower()
        
        for row in range(self.user_table.rowCount()):
            show_row = False
            for col in range(self.user_table.columnCount()):
                item = self.user_table.item(row, col)
                if item and search_text in item.text().lower():
                    show_row = True
                    break
            
            self.user_table.setRowHidden(row, not show_row)
    
    def show_add_user_dialog(self):
        """Yeni kullanıcı ekleme dialogunu gösterir."""
        dialog = UserDialog(self.auth_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()
    
    def show_edit_user_dialog(self):
        """Kullanıcı düzenleme dialogunu gösterir."""
        selected = self.user_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlenecek kullanıcıyı seçin.")
            return

        row = selected[0].row()
        email = self.user_table.item(row, 2).text()
        user = self.auth_manager.get_user(email)
        
        if user:
            dialog = UserDialog(self.auth_manager, user=user, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.load_users()
    
    def delete_user(self):
        """Seçili kullanıcıyı siler."""
        selected = self.user_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek kullanıcıyı seçin.")
            return

        row = selected[0].row()
        email = self.user_table.item(row, 2).text()
        
        reply = QMessageBox.question(
            self,
            "Onay",
            f"{email} kullanıcısını silmek istediğinizden emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.auth_manager.delete_user(email):
                self.load_users()
                QMessageBox.information(self, "Başarılı", "Kullanıcı başarıyla silindi.")
            else:
                QMessageBox.critical(self, "Hata", "Kullanıcı silinirken bir hata oluştu.")

class UserDialog(QDialog):
    """Kullanıcı ekleme/düzenleme dialogu."""
    
    def __init__(self, auth_manager: AuthManager, user=None, parent=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.user = user
        
        self.setWindowTitle('Kullanıcı Ekle' if not self.user else 'Kullanıcı Düzenle')
        self.setMinimumWidth(400)
        
        self.init_ui()
    
    def init_ui(self):
        """Kullanıcı ekleme/düzenleme dialogunu oluşturur."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #424242;
                font-size: 13px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
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
            QPushButton[text="İptal"] {
                background-color: #757575;
            }
            QPushButton[text="İptal"]:hover {
                background-color: #616161;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Form düzeni
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 15px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(10)

        # Kullanıcı bilgileri
        self.first_name_input = QLineEdit(self.user['first_name'] if self.user else '')
        self.first_name_input.setPlaceholderText('Ad')
        form_layout.addWidget(QLabel('Ad:'))
        form_layout.addWidget(self.first_name_input)

        self.last_name_input = QLineEdit(self.user['last_name'] if self.user else '')
        self.last_name_input.setPlaceholderText('Soyad')
        form_layout.addWidget(QLabel('Soyad:'))
        form_layout.addWidget(self.last_name_input)

        self.email_input = QLineEdit(self.user['email'] if self.user else '')
        self.email_input.setPlaceholderText('E-posta')
        form_layout.addWidget(QLabel('E-posta:'))
        form_layout.addWidget(self.email_input)

        self.group_input = QLineEdit(self.user['group'] if self.user else '')
        self.group_input.setPlaceholderText('Grup')
        form_layout.addWidget(QLabel('Grup:'))
        form_layout.addWidget(self.group_input)

        if not self.user:
            self.password_input = QLineEdit()
            self.password_input.setPlaceholderText('Şifre')
            self.password_input.setEchoMode(QLineEdit.Password)
            form_layout.addWidget(QLabel('Şifre:'))
            form_layout.addWidget(self.password_input)

        layout.addWidget(form_frame)

        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        save_button = QPushButton('Kaydet')
        save_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton('İptal')
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def get_user_data(self):
        """Dialog'dan kullanıcı verilerini alır."""
        data = {
            'first_name': self.first_name_input.text(),
            'last_name': self.last_name_input.text(),
            'email': self.email_input.text(),
            'group': self.group_input.text()
        }
        
        if not self.user:
            data['password'] = self.password_input.text()
            
        return data 