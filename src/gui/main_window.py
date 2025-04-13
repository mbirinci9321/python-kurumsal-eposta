import sys
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QMenuBar, QStatusBar, QMessageBox, QDialog,
    QLabel, QLineEdit, QPushButton, QFormLayout,
    QDialogButtonBox, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QToolBar, QComboBox, QFrame
)
from PyQt6.QtCore import Qt, QSize, QMimeData
from PyQt6.QtGui import QAction, QIcon, QDragEnterEvent, QDropEvent, QFont
from utils.data_manager import DataManager
from utils.auth_manager import AuthManager
from utils.logger import Logger
from utils.crypto_manager import CryptoManager
from utils.filters import Filter
from utils.license_manager import LicenseManager
from .user_window import UserWindow
from .license_window import LicenseWindow
from .template_window import TemplateWindow
from .signature_window import SignatureWindow
from .group_window import GroupWindow
from .ad_config_window import ADConfigWindow
from .icons import IconManager
from .shortcuts import ShortcutManager
from .user_management_dialog import UserManagementDialog
from .change_password_dialog import ChangePasswordDialog
from .backup_window import BackupWindow
import os
import json
import shutil

class MainWindow(QMainWindow):
    """Ana pencere sınıfı."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Outlook İmza Yöneticisi")
        self.setMinimumSize(800, 600)
        
        # Veri yöneticisi
        self.data_manager = DataManager()
        
        # Güvenlik yöneticileri
        self.auth_manager = AuthManager()
        self.logger = Logger("main")
        self.crypto_manager = CryptoManager()
        
        # Lisans yöneticisi
        self.license_manager = LicenseManager()
        
        # İkon yöneticisi
        self.icon_manager = IconManager()
        
        # Tema uygula
        self.apply_theme()
        
        # Ana widget ve layout
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        # Üst menü
        self.create_menu_bar()
        
        # Durum çubuğu
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hazır")
        
        # Sekmeleri oluştur
        self.create_tabs()
        
        # Kısayol yöneticisi
        self.shortcut_manager = ShortcutManager(self)
        
        # Verileri yükle
        self.load_data()
        
        self.setAcceptDrops(True)
        
        # İlk giriş kontrolü
        self.check_first_login()
    
    def check_first_login(self):
        """İlk giriş kontrolü yapar"""
        if not self.auth_manager.has_users():
            self.show_first_login_dialog()
    
    def show_first_login_dialog(self):
        """İlk giriş dialogunu gösterir"""
        dialog = QDialog(self)
        dialog.setWindowTitle("İlk Giriş")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Form alanları
        form_layout = QFormLayout()
        
        username_edit = QLineEdit()
        form_layout.addRow("Kullanıcı Adı:", username_edit)
        
        password_edit = QLineEdit()
        password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Şifre:", password_edit)
        
        confirm_password_edit = QLineEdit()
        confirm_password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Şifre Tekrar:", confirm_password_edit)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(lambda: self.handle_first_login(
            dialog, username_edit.text(), password_edit.text(), confirm_password_edit.text()
        ))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def handle_first_login(self, dialog, username, password, confirm_password):
        """İlk giriş işlemini yönetir"""
        if not username or not password:
            QMessageBox.warning(dialog, "Hata", "Kullanıcı adı ve şifre boş olamaz!")
            return
            
        if password != confirm_password:
            QMessageBox.warning(dialog, "Hata", "Şifreler eşleşmiyor!")
            return
            
        if self.auth_manager.register(username, password, "admin"):
            self.logger.log_security("İlk admin kullanıcısı oluşturuldu", username)
            dialog.accept()
        else:
            QMessageBox.critical(dialog, "Hata", "Kullanıcı oluşturulurken bir hata oluştu!")
    
    def apply_theme(self):
        """Tema dosyasını yükler ve uygular."""
        theme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "themes", "default.qss")
        try:
            with open(theme_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print(f"Tema dosyası bulunamadı: {theme_path}")
        except Exception as e:
            print(f"Tema yüklenirken hata oluştu: {e}")
    
    def create_menu_bar(self):
        """Üst menüyü oluşturur."""
        menu_bar = self.menuBar()
        
        # Dosya menüsü
        file_menu = menu_bar.addMenu("Dosya")
        
        save_action = QAction("Kaydet", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_data)
        self.icon_manager.set_icon(save_action, "save")
        file_menu.addAction(save_action)
        
        refresh_action = QAction("Yenile", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_all)
        self.icon_manager.set_icon(refresh_action, "refresh")
        file_menu.addAction(refresh_action)
        
        backup_action = QAction("Yedekleme Yönetimi", self)
        backup_action.setShortcut("Ctrl+B")
        backup_action.triggered.connect(self.show_backup_window)
        self.icon_manager.set_icon(backup_action, "backup")
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Çıkış", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        self.icon_manager.set_icon(exit_action, "quit")
        file_menu.addAction(exit_action)
        
        # Düzen menüsü
        edit_menu = menu_bar.addMenu("Düzen")
        
        add_action = QAction("Ekle", self)
        add_action.setShortcut("Ctrl+N")
        add_action.triggered.connect(self.add_item)
        self.icon_manager.set_icon(add_action, "add")
        edit_menu.addAction(add_action)
        
        edit_action = QAction("Düzenle", self)
        edit_action.setShortcut("Ctrl+E")
        edit_action.triggered.connect(self.edit_item)
        self.icon_manager.set_icon(edit_action, "edit")
        edit_menu.addAction(edit_action)
        
        delete_action = QAction("Sil", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.delete_item)
        self.icon_manager.set_icon(delete_action, "delete")
        edit_menu.addAction(delete_action)
        
        # Görünüm menüsü
        view_menu = menu_bar.addMenu("Görünüm")
        
        search_action = QAction("Ara", self)
        search_action.setShortcut("Ctrl+F")
        search_action.triggered.connect(self.show_search)
        self.icon_manager.set_icon(search_action, "search")
        view_menu.addAction(search_action)
        
        filter_action = QAction("Filtrele", self)
        filter_action.setShortcut("Ctrl+L")
        filter_action.triggered.connect(self.show_filter)
        self.icon_manager.set_icon(filter_action, "filter")
        view_menu.addAction(filter_action)
        
        # Yardım menüsü
        help_menu = menu_bar.addMenu("Yardım")
        
        about_action = QAction("Hakkında", self)
        about_action.setShortcut("F1")
        about_action.triggered.connect(self.show_about_dialog)
        self.icon_manager.set_icon(about_action, "info")
        help_menu.addAction(about_action)
        
        # Güvenlik menüsü
        security_menu = menu_bar.addMenu("Güvenlik")
        
        change_password_action = QAction("Şifre Değiştir", self)
        change_password_action.triggered.connect(self.show_change_password_dialog)
        self.icon_manager.set_icon(change_password_action, "security")
        security_menu.addAction(change_password_action)
        
        if self.auth_manager.has_permission(self.auth_manager.current_user_id, "manage_users"):
            user_management_action = QAction("Kullanıcı Yönetimi", self)
            user_management_action.triggered.connect(self.show_user_management_dialog)
            self.icon_manager.set_icon(user_management_action, "users")
            security_menu.addAction(user_management_action)
        
        # İmza menüsü
        signature_menu = menu_bar.addMenu("İmza")
        
        manage_signatures_action = QAction("İmza Yönetimi", self)
        manage_signatures_action.triggered.connect(self.show_signature_window)
        self.icon_manager.set_icon(manage_signatures_action, "file")
        signature_menu.addAction(manage_signatures_action)
        
        # Grup menüsü
        group_menu = menu_bar.addMenu("Grup")
        
        manage_groups_action = QAction("Grup Yönetimi", self)
        manage_groups_action.triggered.connect(self.show_group_window)
        self.icon_manager.set_icon(manage_groups_action, "group")
        group_menu.addAction(manage_groups_action)
        
        # Active Directory menüsü
        ad_menu = menu_bar.addMenu("Active Directory")
        
        ad_config_action = QAction("AD Yapılandırma", self)
        ad_config_action.triggered.connect(self.show_ad_config_window)
        self.icon_manager.set_icon(ad_config_action, "server")
        ad_menu.addAction(ad_config_action)
        
        ad_management_action = QAction("AD Kullanıcı Yönetimi", self)
        ad_management_action.triggered.connect(self.show_ad_management_window)
        self.icon_manager.set_icon(ad_management_action, "users")
        ad_menu.addAction(ad_management_action)
        
        # Lisans menüsü
        license_menu = menu_bar.addMenu("Lisans")
        
        manage_licenses_action = QAction("Lisans Yönetimi", self)
        manage_licenses_action.triggered.connect(self.show_license_window)
        self.icon_manager.set_icon(manage_licenses_action, "license")
        license_menu.addAction(manage_licenses_action)
    
    def create_tabs(self):
        """Tab widget'larını oluşturur."""
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #F5F5F5;
                color: #424242;
                padding: 8px 16px;
                border: 1px solid #E0E0E0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: none;
            }
            QTabBar::tab:hover:!selected {
                background-color: #FAFAFA;
            }
        """)

        # İmza yönetimi sekmesi
        self.signature_window = SignatureWindow(parent=self)
        self.tab_widget.addTab(self.signature_window, "İmza Yönetimi")

        # Grup yönetimi sekmesi
        self.group_window = GroupWindow(self.data_manager, parent=self)
        self.tab_widget.addTab(self.group_window, "Grup Yönetimi")

        # Lisans yönetimi sekmesi
        self.license_window = LicenseWindow(parent=self)
        self.tab_widget.addTab(self.license_window, "Lisans Yönetimi")

        self.setCentralWidget(self.tab_widget)
    
    def load_data(self):
        """Tüm verileri yükler."""
        try:
            self.data_manager.load_data()
            
            # Sadece var olan pencereler için veri yükleme işlemi yap
            if hasattr(self, 'signature_window'):
                self.signature_window.load_signatures()
            
            if hasattr(self, 'group_window'):
                self.group_window.load_groups()
            
            if hasattr(self, 'license_window'):
                self.license_window.load_licenses()
            
            self.status_bar.showMessage("Veriler başarıyla yüklendi", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veriler yüklenirken bir hata oluştu: {str(e)}")
    
    def show_about_dialog(self):
        """Hakkında penceresini gösterir."""
        QMessageBox.about(
            self,
            "Hakkında",
            "Outlook İmza Yöneticisi v1.0\n\n"
            "Bu uygulama, şirket çalışanlarının Outlook imzalarını "
            "merkezi olarak yönetmek için geliştirilmiştir."
        )
    
    def create_toolbar(self):
        """Üst toolbar'ı oluşturur."""
        toolbar_layout = QHBoxLayout()
        
        # Yeni kullanıcı butonu
        self.new_user_btn = QPushButton("Yeni Kullanıcı")
        self.new_user_btn.clicked.connect(self.show_new_user_dialog)
        toolbar_layout.addWidget(self.new_user_btn)
        
        # Yeni şablon butonu
        self.new_template_btn = QPushButton("Yeni Şablon")
        self.new_template_btn.clicked.connect(self.show_new_template_dialog)
        toolbar_layout.addWidget(self.new_template_btn)
        
        # Şablon yönetimi butonu
        self.template_btn = QPushButton("Şablon Yönetimi")
        self.template_btn.clicked.connect(self.show_template_window)
        toolbar_layout.addWidget(self.template_btn)
        
        # Lisans yönetimi butonu
        self.license_btn = QPushButton("Lisans Yönetimi")
        self.license_btn.clicked.connect(self.show_license_dialog)
        toolbar_layout.addWidget(self.license_btn)
        
        # Ayarlar butonu
        self.settings_btn = QPushButton("Ayarlar")
        self.settings_btn.clicked.connect(self.show_settings_dialog)
        toolbar_layout.addWidget(self.settings_btn)
        
        self.main_layout.addLayout(toolbar_layout)
    
    def create_filter_area(self):
        """Filtreleme alanını oluşturur."""
        filter_layout = QFormLayout()
        
        # Departman filtresi
        self.department_combo = QComboBox()
        self.department_combo.addItem("Tümü")
        self.department_combo.addItems(self.data_manager.get_departments())
        self.department_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addRow("Departman:", self.department_combo)
        
        # Rol filtresi
        self.role_combo = QComboBox()
        self.role_combo.addItem("Tümü")
        self.role_combo.addItems(self.data_manager.get_roles())
        self.role_combo.currentTextChanged.connect(self.apply_filters)
        filter_layout.addRow("Rol:", self.role_combo)
        
        # Arama kutusu
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("İsim veya e-posta ile ara...")
        self.search_edit.textChanged.connect(self.apply_filters)
        filter_layout.addRow("Ara:", self.search_edit)
        
        self.main_layout.addLayout(filter_layout)
    
    def create_user_table(self):
        """Kullanıcı tablosunu oluşturur."""
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels([
            "ID", "Ad Soyad", "E-posta", "Departman", "Rol", "Durum"
        ])
        self.user_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.user_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.user_table.itemDoubleClicked.connect(self.show_user_details)
        
        self.main_layout.addWidget(self.user_table)
    
    def create_bottom_toolbar(self):
        """Alt toolbar'ı oluşturur."""
        bottom_layout = QHBoxLayout()
        
        # Durum etiketi
        self.status_label = QLabel("Toplam 0 kullanıcı")
        bottom_layout.addWidget(self.status_label)
        
        # Sayfalama butonları
        self.prev_page_btn = QPushButton("Önceki")
        self.prev_page_btn.clicked.connect(self.prev_page)
        bottom_layout.addWidget(self.prev_page_btn)
        
        self.next_page_btn = QPushButton("Sonraki")
        self.next_page_btn.clicked.connect(self.next_page)
        bottom_layout.addWidget(self.next_page_btn)
        
        self.main_layout.addLayout(bottom_layout)
    
    def load_users(self):
        """Kullanıcıları yükler ve tabloya ekler."""
        users = self.data_manager.get_users()
        self.filtered_users = users
        self.update_user_table()
    
    def apply_filters(self):
        """Filtreleri uygular."""
        department = self.department_combo.currentText()
        role = self.role_combo.currentText()
        search_text = self.search_edit.text().lower()
        
        # Departman ve rol filtreleri
        if department != "Tümü" or role != "Tümü":
            self.filtered_users = Filter.filter_users(
                self.data_manager.get_users(),
                department=department if department != "Tümü" else None,
                role=role if role != "Tümü" else None
            )
        else:
            self.filtered_users = self.data_manager.get_users()
        
        # Arama filtresi
        if search_text:
            self.filtered_users = [
                user for user in self.filtered_users
                if search_text in user["full_name"].lower() or
                   search_text in user["email"].lower()
            ]
        
        self.update_user_table()
    
    def update_user_table(self):
        """Kullanıcı tablosunu günceller."""
        self.user_table.setRowCount(len(self.filtered_users))
        
        for row, user in enumerate(self.filtered_users):
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user["id"])))
            self.user_table.setItem(row, 1, QTableWidgetItem(user["full_name"]))
            self.user_table.setItem(row, 2, QTableWidgetItem(user["email"]))
            self.user_table.setItem(row, 3, QTableWidgetItem(user["department"]))
            self.user_table.setItem(row, 4, QTableWidgetItem(user["role"]))
            self.user_table.setItem(row, 5, QTableWidgetItem(
                "Aktif" if user["is_active"] else "Pasif"
            ))
        
        self.status_label.setText(f"Toplam {len(self.filtered_users)} kullanıcı")
    
    def show_new_user_dialog(self):
        """Yeni kullanıcı ekleme dialogunu gösterir."""
        QMessageBox.information(
            self,
            "Bilgi",
            "Yeni kullanıcı ekleme özelliği henüz uygulanmadı."
        )
    
    def show_new_template_dialog(self):
        """Yeni şablon ekleme dialogunu gösterir."""
        QMessageBox.information(
            self,
            "Bilgi",
            "Yeni şablon ekleme özelliği henüz uygulanmadı."
        )
    
    def show_template_window(self):
        """Şablon yönetimi penceresini gösterir."""
        self.template_tab = TemplateWindow()
        self.template_tab.show()
    
    def show_license_dialog(self):
        """Lisans yönetimi dialogunu gösterir."""
        QMessageBox.information(
            self,
            "Bilgi",
            "Lisans yönetimi özelliği henüz uygulanmadı."
        )
    
    def show_settings_dialog(self):
        """Ayarlar dialogunu gösterir."""
        QMessageBox.information(
            self,
            "Bilgi",
            "Ayarlar özelliği henüz uygulanmadı."
        )
    
    def show_user_details(self, item):
        """Kullanıcı detaylarını gösterir."""
        row = item.row()
        user_id = int(self.user_table.item(row, 0).text())
        user = self.data_manager.get_user_by_id(user_id)
        
        QMessageBox.information(
            self,
            "Kullanıcı Detayları",
            f"ID: {user['id']}\n"
            f"Ad Soyad: {user['full_name']}\n"
            f"E-posta: {user['email']}\n"
            f"Departman: {user['department']}\n"
            f"Rol: {user['role']}\n"
            f"Durum: {'Aktif' if user['is_active'] else 'Pasif'}"
        )
    
    def prev_page(self):
        """Önceki sayfaya geçer."""
        # Sayfalama henüz uygulanmadı
        pass
    
    def next_page(self):
        """Sonraki sayfaya geçer."""
        # Sayfalama henüz uygulanmadı
        pass
    
    def backup_data(self):
        """Verileri yedekler."""
        # TODO: Yedekleme işlemi
        self.status_bar.showMessage("Veriler yedeklendi", 3000)
    
    def restore_data(self):
        """Yedekten verileri geri yükler."""
        # TODO: Geri yükleme işlemi
        self.status_bar.showMessage("Veriler geri yüklendi", 3000)
    
    def refresh_all(self):
        """Tüm veriyi yeniler."""
        self.data_manager.load_all_data()
        
        # Sekmeleri yenilemek için özel metodları çağır
        if hasattr(self, 'signature_window'):
            self.signature_window.load_signatures()
            
        if hasattr(self, 'group_window'):
            self.group_window.load_groups()
            
        if hasattr(self, 'license_window'):
            self.license_window.load_licenses()
        
        self.logger.log_operation("refresh", "all_data")
        self.status_bar.showMessage("Tüm veriler yenilendi", 3000)
    
    def save_data(self):
        """Verileri kaydeder."""
        try:
            self.data_manager.save_all()
            self.logger.log_operation("save", "all_data")
            self.status_bar.showMessage("Veriler kaydedildi", 3000)
        except Exception as e:
            self.logger.log_error("save", "all_data", e)
            QMessageBox.critical(self, "Hata", f"Veriler kaydedilirken hata oluştu: {str(e)}")
    
    def show_backup_window(self):
        """Yedekleme penceresini gösterir."""
        self.backup_window = BackupWindow(self.data_manager)
        self.backup_window.show()
    
    def show_change_password_dialog(self):
        """Şifre değiştirme dialogunu gösterir"""
        dialog = ChangePasswordDialog(self.auth_manager, self.logger, self)
        dialog.exec()
    
    def show_user_management_dialog(self):
        """Kullanıcı yönetimi dialogunu gösterir"""
        dialog = UserManagementDialog(self.auth_manager, self.logger, self)
        dialog.exec()
    
    def show_signature_window(self):
        """İmza yönetimi penceresini gösterir."""
        self.signature_window = SignatureWindow(self.data_manager)
        self.signature_window.show()
    
    def show_group_window(self):
        """Grup yönetimi penceresini gösterir."""
        self.group_tab = GroupWindow(self.data_manager)
        self.group_tab.show()
    
    def show_license_window(self):
        """Lisans yönetimi penceresini gösterir."""
        self.license_window = LicenseWindow(parent=self)
        self.license_window.show()
    
    def show_ad_config_window(self):
        """AD yapılandırma penceresini gösterir."""
        self.ad_config_window = ADConfigWindow(self)
        self.ad_config_window.show()
    
    def show_ad_management_window(self):
        """AD yönetim penceresini gösterir."""
        self.ad_config_window = ADConfigWindow(self)
        self.ad_config_window.show()
    
    def closeEvent(self, event):
        """Pencere kapatıldığında çalışır."""
        reply = QMessageBox.question(
            self,
            "Çıkış",
            "Uygulamadan çıkmak istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logger.log_operation("close", "application")
            event.accept()
        else:
            event.ignore()

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Sürükleme olayını işler"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Bırakma olayını işler"""
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        for file in files:
            if file.endswith('.json'):
                self.import_data(file)
            elif file.endswith(('.png', '.jpg', '.jpeg')):
                self.import_image(file)

    def import_data(self, file_path: str):
        """JSON dosyasını içe aktarır"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, list):
                for item in data:
                    if 'type' in item:
                        if item['type'] == 'user':
                            self.data_manager.add_user(item)
                        elif item['type'] == 'license':
                            self.data_manager.add_license(item)
                        elif item['type'] == 'template':
                            self.data_manager.add_template(item)
                
                QMessageBox.information(self, "Başarılı", "Veriler başarıyla içe aktarıldı.")
                self.refresh_all()
            else:
                QMessageBox.warning(self, "Uyarı", "Geçersiz veri formatı.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Veri içe aktarılırken hata oluştu: {str(e)}")

    def import_image(self, file_path: str):
        """Resim dosyasını içe aktarır"""
        try:
            # Resmi assets/icons dizinine kopyala
            file_name = os.path.basename(file_path)
            target_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", file_name)
            shutil.copy2(file_path, target_path)
            
            QMessageBox.information(self, "Başarılı", "Resim başarıyla içe aktarıldı.")
            # İkonları yenile
            self.icon_manager = IconManager()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Resim içe aktarılırken hata oluştu: {str(e)}")

    def add_item(self):
        """Seçili sekmeye yeni öğe ekler."""
        current_tab = self.central_widget.currentWidget()
        if isinstance(current_tab, UserWindow):
            current_tab.show_add_user_dialog()
        elif isinstance(current_tab, LicenseWindow):
            current_tab.show_add_license_dialog()
        elif isinstance(current_tab, TemplateWindow):
            current_tab.show_add_template_dialog()
        elif isinstance(current_tab, SignatureWindow):
            current_tab.show_add_signature_dialog()
    
    def edit_item(self):
        """Seçili öğeyi düzenler."""
        current_tab = self.central_widget.currentWidget()
        if isinstance(current_tab, UserWindow):
            current_tab.show_edit_user_dialog()
        elif isinstance(current_tab, LicenseWindow):
            current_tab.show_edit_license_dialog()
        elif isinstance(current_tab, TemplateWindow):
            current_tab.show_edit_template_dialog()
        elif isinstance(current_tab, SignatureWindow):
            current_tab.show_edit_signature_dialog()
    
    def delete_item(self):
        """Seçili öğeyi siler."""
        current_tab = self.central_widget.currentWidget()
        if isinstance(current_tab, UserWindow):
            current_tab.delete_user()
        elif isinstance(current_tab, LicenseWindow):
            current_tab.delete_license()
        elif isinstance(current_tab, TemplateWindow):
            current_tab.delete_template()
        elif isinstance(current_tab, SignatureWindow):
            current_tab.delete_signature()
    
    def show_search(self):
        """Arama dialogunu gösterir."""
        current_tab = self.central_widget.currentWidget()
        if hasattr(current_tab, "search_edit"):
            current_tab.search_edit.setFocus()
    
    def show_filter(self):
        """Filtre dialogunu gösterir."""
        current_tab = self.central_widget.currentWidget()
        if hasattr(current_tab, "filter_combo"):
            current_tab.filter_combo.setFocus() 