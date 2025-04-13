from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFormLayout,
    QMessageBox, QGroupBox, QComboBox, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QDialog, QDialogButtonBox, QSpinBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from src.utils.active_directory import ActiveDirectoryManager

class ADConfigDialog(QDialog):
    """Active Directory yapılandırması için dialog."""
    
    def __init__(self, ad_manager, parent=None):
        super().__init__(parent)
        self.ad_manager = ad_manager
        self.setWindowTitle("Active Directory Yapılandırması")
        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        self.init_ui()
        
    def init_ui(self):
        """Dialog arayüzünü oluşturur."""
        layout = QVBoxLayout(self)
        
        # Bağlantı ayarları
        connection_group = QGroupBox("Bağlantı Ayarları")
        form_layout = QFormLayout()
        
        self.server_edit = QLineEdit(self.ad_manager.config.get("server", ""))
        form_layout.addRow("Sunucu:", self.server_edit)
        
        self.domain_edit = QLineEdit(self.ad_manager.config.get("domain", ""))
        form_layout.addRow("Domain:", self.domain_edit)
        
        self.base_dn_edit = QLineEdit(self.ad_manager.config.get("base_dn", ""))
        form_layout.addRow("Base DN:", self.base_dn_edit)
        
        self.username_edit = QLineEdit(self.ad_manager.config.get("username", ""))
        form_layout.addRow("Kullanıcı Adı:", self.username_edit)
        
        self.password_edit = QLineEdit(self.ad_manager.config.get("password", ""))
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Şifre:", self.password_edit)
        
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(self.ad_manager.config.get("port", 389))
        form_layout.addRow("Port:", self.port_spin)
        
        self.ssl_check = QCheckBox("SSL Kullan")
        self.ssl_check.setChecked(self.ad_manager.config.get("use_ssl", False))
        form_layout.addRow("", self.ssl_check)
        
        self.tls_check = QCheckBox("TLS Kullan")
        self.tls_check.setChecked(self.ad_manager.config.get("use_tls", False))
        form_layout.addRow("", self.tls_check)
        
        connection_group.setLayout(form_layout)
        layout.addWidget(connection_group)
        
        # Test butonu
        test_button = QPushButton("Bağlantıyı Test Et")
        test_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        test_button.clicked.connect(self.test_connection)
        layout.addWidget(test_button)
        
        # Butonlar
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def test_connection(self):
        """AD bağlantısını test eder."""
        self.update_ad_config()
        
        result = self.ad_manager.test_connection()
        
        if result["success"]:
            details = result.get("details", {})
            message = (
                f"Active Directory bağlantısı başarılı!\n\n"
                f"Domain: {details.get('server_info', {}).get('domain', '')}\n"
                f"OU Sayısı: {details.get('ou_count', 0)}\n"
                f"Kullanıcı Sayısı: {details.get('user_count', 0)}"
            )
            QMessageBox.information(self, "Başarılı", message)
        else:
            QMessageBox.critical(self, "Hata", f"Bağlantı başarısız: {result.get('message', '')}")
    
    def update_ad_config(self):
        """AD yapılandırmasını günceller."""
        self.ad_manager.config["server"] = self.server_edit.text()
        self.ad_manager.config["domain"] = self.domain_edit.text()
        self.ad_manager.config["base_dn"] = self.base_dn_edit.text()
        self.ad_manager.config["username"] = self.username_edit.text()
        self.ad_manager.config["password"] = self.password_edit.text()
        self.ad_manager.config["port"] = self.port_spin.value()
        self.ad_manager.config["use_ssl"] = self.ssl_check.isChecked()
        self.ad_manager.config["use_tls"] = self.tls_check.isChecked()
    
    def accept(self):
        """Dialog kabul edildiğinde çağrılır."""
        self.update_ad_config()
        
        if self.ad_manager.save_config():
            super().accept()
        else:
            QMessageBox.critical(self, "Hata", "Yapılandırma kaydedilemedi!")

class ADConfigWindow(QMainWindow):
    """Active Directory yapılandırma ve yönetim penceresi."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ad_manager = ActiveDirectoryManager()
        self.setWindowTitle("Active Directory Yönetimi")
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        self.main_layout = QVBoxLayout(central_widget)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Pencere arayüzünü oluşturur."""
        # Üst toolbar
        toolbar = QHBoxLayout()
        
        self.config_button = QPushButton("Yapılandırma")
        self.config_button.clicked.connect(self.show_config_dialog)
        toolbar.addWidget(self.config_button)
        
        self.refresh_button = QPushButton("Yenile")
        self.refresh_button.clicked.connect(self.load_data)
        toolbar.addWidget(self.refresh_button)
        
        self.main_layout.addLayout(toolbar)
        
        # OU seçici
        ou_layout = QHBoxLayout()
        ou_layout.addWidget(QLabel("Organizational Unit:"))
        
        self.ou_combo = QComboBox()
        self.ou_combo.currentIndexChanged.connect(self.on_ou_changed)
        ou_layout.addWidget(self.ou_combo)
        
        self.main_layout.addLayout(ou_layout)
        
        # Kullanıcı tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Kullanıcı Adı", "Ad Soyad", "E-posta", "Departman", "Ünvan"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.main_layout.addWidget(self.table)
        
        # İmza atama butonları
        signature_layout = QHBoxLayout()
        
        signature_layout.addWidget(QLabel("İmza Şablonu:"))
        
        self.signature_combo = QComboBox()
        signature_layout.addWidget(self.signature_combo)
        
        self.apply_button = QPushButton("Seçili Kullanıcılara İmzayı Uygula")
        self.apply_button.clicked.connect(self.apply_signature_to_selected)
        signature_layout.addWidget(self.apply_button)
        
        self.apply_all_button = QPushButton("Tüm OU'ya İmzayı Uygula")
        self.apply_all_button.clicked.connect(self.apply_signature_to_ou)
        signature_layout.addWidget(self.apply_all_button)
        
        self.main_layout.addLayout(signature_layout)
        
        # Veri yükle
        self.load_data()
        
    def show_config_dialog(self):
        """AD yapılandırma dialogunu gösterir."""
        dialog = ADConfigDialog(self.ad_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()
    
    def load_data(self):
        """AD verilerini yükler."""
        # Önce bağlantıyı test et
        if not self.ad_manager.connect():
            QMessageBox.warning(
                self,
                "Bağlantı Hatası",
                "Active Directory'e bağlanılamadı. Lütfen yapılandırma ayarlarını kontrol edin."
            )
            return
        
        # OU'ları yükle
        self.ou_combo.clear()
        ous = self.ad_manager.get_all_ous()
        
        # Base DN'i ekle
        base_dn = self.ad_manager.config.get("base_dn", "")
        if base_dn:
            self.ou_combo.addItem("Tüm Domain", base_dn)
        
        # Diğer OU'ları ekle
        for ou in ous:
            name = ou.get("name", "")
            dn = ou.get("distinguishedName", "")
            if name and dn:
                self.ou_combo.addItem(name, dn)
        
        # İmza şablonlarını yükle
        self.signature_combo.clear()
        
        # Ana pencereden imza yöneticisini al
        from src.utils.signature_manager import SignatureManager
        signature_manager = None
        
        main_window = self.parent()
        if main_window and hasattr(main_window, 'data_manager'):
            signature_manager = SignatureManager(main_window.data_manager)
        else:
            from src.utils.data_manager import DataManager
            data_manager = DataManager()
            signature_manager = SignatureManager(data_manager)
        
        templates = signature_manager.get_all_signature_templates()
        for template in templates:
            self.signature_combo.addItem(template.get("name", ""), template.get("id", ""))
        
        # İlk OU'yu seç ve kullanıcıları yükle
        if self.ou_combo.count() > 0:
            self.ou_combo.setCurrentIndex(0)
            self.load_users_from_current_ou()
    
    def on_ou_changed(self, index):
        """OU değiştiğinde kullanıcıları yükler."""
        self.load_users_from_current_ou()
    
    def load_users_from_current_ou(self):
        """Seçili OU'dan kullanıcıları yükler."""
        ou_dn = self.ou_combo.currentData()
        if not ou_dn:
            return
        
        # Kullanıcıları yükle
        users = self.ad_manager.get_users_from_ou(ou_dn)
        
        # Tabloyu temizle
        self.table.setRowCount(0)
        
        # Kullanıcıları tabloya ekle
        for user in users:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(user.get("sAMAccountName", "")))
            self.table.setItem(row, 1, QTableWidgetItem(user.get("displayName", "")))
            self.table.setItem(row, 2, QTableWidgetItem(user.get("mail", "")))
            self.table.setItem(row, 3, QTableWidgetItem(user.get("department", "")))
            self.table.setItem(row, 4, QTableWidgetItem(user.get("title", "")))
    
    def apply_signature_to_selected(self):
        """Seçili kullanıcılara imza şablonunu uygular."""
        # Seçili satırları kontrol et
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir kullanıcı seçin.")
            return
        
        # Seçili imza şablonunu kontrol et
        template_id = self.signature_combo.currentData()
        if not template_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir imza şablonu seçin.")
            return
        
        # Seçili kullanıcıları al
        users = []
        ou_dn = self.ou_combo.currentData()
        all_users = self.ad_manager.get_users_from_ou(ou_dn)
        
        for row in selected_rows:
            username = self.table.item(row, 0).text()
            # Kullanıcıyı tüm kullanıcılar listesinde bul
            user = next((u for u in all_users if u.get("sAMAccountName") == username), None)
            if user:
                users.append(user)
        
        if not users:
            QMessageBox.warning(self, "Uyarı", "Seçili kullanıcılar bulunamadı.")
            return
        
        # İmza şablonunu al
        from src.utils.signature_manager import SignatureManager
        signature_manager = None
        
        main_window = self.parent()
        if main_window and hasattr(main_window, 'data_manager'):
            signature_manager = SignatureManager(main_window.data_manager)
        else:
            from src.utils.data_manager import DataManager
            data_manager = DataManager()
            signature_manager = SignatureManager(data_manager)
        
        template = signature_manager.get_signature_template(template_id)
        
        if not template:
            QMessageBox.warning(self, "Uyarı", "İmza şablonu bulunamadı.")
            return
        
        # İmzaları uygula
        from src.utils.outlook_manager import OutlookManager
        outlook_manager = OutlookManager()
        
        result = outlook_manager.apply_signatures_to_users(users, template)
        
        # Sonuçları göster
        success_count = len(result.get("success", []))
        failed_count = len(result.get("failed", []))
        
        message = f"İmza uygulaması tamamlandı.\n\nBaşarılı: {success_count} kullanıcı\nBaşarısız: {failed_count} kullanıcı"
        
        if failed_count > 0:
            # Hata detaylarını göster
            message += "\n\nHatalı Kullanıcılar:"
            for failed in result.get("failed", []):
                message += f"\n- {failed.get('display_name', failed.get('user_id', 'Bilinmeyen'))}: {failed.get('error', 'Bilinmeyen hata')}"
        
        if success_count > 0:
            QMessageBox.information(self, "Başarılı", message)
        else:
            QMessageBox.critical(self, "Hata", message)
    
    def apply_signature_to_ou(self):
        """Seçili OU'daki tüm kullanıcılara imza şablonunu uygular."""
        # Seçili OU'yu kontrol et
        ou_dn = self.ou_combo.currentData()
        if not ou_dn:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir OU seçin.")
            return
        
        # Seçili imza şablonunu kontrol et
        template_id = self.signature_combo.currentData()
        if not template_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir imza şablonu seçin.")
            return
        
        # İmza şablonunu al
        from src.utils.signature_manager import SignatureManager
        signature_manager = None
        
        main_window = self.parent()
        if main_window and hasattr(main_window, 'data_manager'):
            signature_manager = SignatureManager(main_window.data_manager)
        else:
            from src.utils.data_manager import DataManager
            data_manager = DataManager()
            signature_manager = SignatureManager(data_manager)
        
        template = signature_manager.get_signature_template(template_id)
        
        if not template:
            QMessageBox.warning(self, "Uyarı", "İmza şablonu bulunamadı.")
            return
        
        # Onay iste
        ou_name = self.ou_combo.currentText()
        reply = QMessageBox.question(
            self,
            "Onay",
            f"{ou_name} içindeki tüm kullanıcılara '{template.get('name', '')}' şablonunu uygulamak istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # İmzaları uygula
        from src.utils.outlook_manager import OutlookManager
        outlook_manager = OutlookManager()
        
        result = outlook_manager.apply_signatures_to_ou(ou_dn, template, self.ad_manager)
        
        # Sonuçları göster
        success_count = len(result.get("success", []))
        failed_count = len(result.get("failed", []))
        
        message = f"İmza uygulaması tamamlandı.\n\nBaşarılı: {success_count} kullanıcı\nBaşarısız: {failed_count} kullanıcı"
        
        if failed_count > 0:
            # Hata detaylarını göster
            message += "\n\nHatalı Kullanıcılar:"
            for failed in result.get("failed", []):
                if "ou_path" in failed:
                    message += f"\n- OU: {failed.get('ou_path', '')}: {failed.get('error', 'Bilinmeyen hata')}"
                else:
                    message += f"\n- {failed.get('display_name', failed.get('user_id', 'Bilinmeyen'))}: {failed.get('error', 'Bilinmeyen hata')}"
        
        if success_count > 0:
            QMessageBox.information(self, "Başarılı", message)
        else:
            QMessageBox.critical(self, "Hata", message) 