from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from utils.data_manager import DataManager
from utils.filters import Filter

class MainWindow(QMainWindow):
    """Ana pencere sınıfı."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Outlook İmza Yönetimi")
        self.setMinimumSize(800, 600)
        
        # Veri yöneticisini başlat
        self.data_manager = DataManager()
        self.data_manager.load_data()
        
        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Üst toolbar
        self.create_toolbar()
        
        # Filtreleme alanı
        self.create_filter_area()
        
        # Kullanıcı tablosu
        self.create_user_table()
        
        # Alt toolbar
        self.create_bottom_toolbar()
        
        # Verileri yükle
        self.load_users()
    
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