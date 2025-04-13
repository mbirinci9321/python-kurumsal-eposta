from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt6.QtCore import Qt

class CategoryDialog(QDialog):
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("Kategori Yönetimi")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Kategori tablosu
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(3)
        self.category_table.setHorizontalHeaderLabels(["ID", "Ad", "Açıklama"])
        self.category_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.category_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.category_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.category_table)

        # Form alanları
        form_layout = QHBoxLayout()
        
        # Sol taraf - Kategori bilgileri
        left_layout = QVBoxLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Kategori adı")
        left_layout.addWidget(QLabel("Kategori Adı:"))
        left_layout.addWidget(self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Kategori açıklaması")
        self.description_edit.setMaximumHeight(100)
        left_layout.addWidget(QLabel("Açıklama:"))
        left_layout.addWidget(self.description_edit)
        
        # Sağ taraf - Butonlar
        right_layout = QVBoxLayout()
        self.add_button = QPushButton("Ekle")
        self.add_button.clicked.connect(self.add_category)
        right_layout.addWidget(self.add_button)
        
        self.update_button = QPushButton("Güncelle")
        self.update_button.clicked.connect(self.update_category)
        self.update_button.setEnabled(False)
        right_layout.addWidget(self.update_button)
        
        self.delete_button = QPushButton("Sil")
        self.delete_button.clicked.connect(self.delete_category)
        self.delete_button.setEnabled(False)
        right_layout.addWidget(self.delete_button)
        
        form_layout.addLayout(left_layout)
        form_layout.addLayout(right_layout)
        layout.addLayout(form_layout)

        self.setLayout(layout)
        self.load_categories()
        
        # Tablo seçim değişikliğini bağla
        self.category_table.itemSelectionChanged.connect(self.on_selection_changed)

    def load_categories(self):
        """Kategorileri yükler ve tabloyu günceller."""
        categories = self.data_manager.get_categories()
        self.category_table.setRowCount(len(categories))
        
        for row, category in enumerate(categories):
            self.category_table.setItem(row, 0, QTableWidgetItem(category["id"]))
            self.category_table.setItem(row, 1, QTableWidgetItem(category["name"]))
            self.category_table.setItem(row, 2, QTableWidgetItem(category["description"]))

    def on_selection_changed(self):
        """Tablo seçimi değiştiğinde form alanlarını günceller."""
        selected_row = self.category_table.currentRow()
        if selected_row >= 0:
            category_id = self.category_table.item(selected_row, 0).text()
            category = self.data_manager.get_category_by_id(category_id)
            
            if category:
                self.name_edit.setText(category["name"])
                self.description_edit.setText(category["description"])
                self.update_button.setEnabled(True)
                self.delete_button.setEnabled(True)
                self.add_button.setEnabled(False)
        else:
            self.clear_form()
            self.update_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.add_button.setEnabled(True)

    def clear_form(self):
        """Form alanlarını temizler."""
        self.name_edit.clear()
        self.description_edit.clear()

    def add_category(self):
        """Yeni kategori ekler."""
        name = self.name_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Uyarı", "Kategori adı boş olamaz!")
            return
        
        try:
            self.data_manager.add_category(name, description)
            self.load_categories()
            self.clear_form()
            QMessageBox.information(self, "Başarılı", "Kategori başarıyla eklendi.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kategori eklenirken bir hata oluştu: {str(e)}")

    def update_category(self):
        """Seçili kategoriyi günceller."""
        selected_row = self.category_table.currentRow()
        if selected_row < 0:
            return
        
        category_id = self.category_table.item(selected_row, 0).text()
        name = self.name_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Uyarı", "Kategori adı boş olamaz!")
            return
        
        try:
            if self.data_manager.update_category(category_id, name, description):
                self.load_categories()
                self.clear_form()
                QMessageBox.information(self, "Başarılı", "Kategori başarıyla güncellendi.")
            else:
                QMessageBox.warning(self, "Uyarı", "Kategori güncellenirken bir hata oluştu.")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kategori güncellenirken bir hata oluştu: {str(e)}")

    def delete_category(self):
        """Seçili kategoriyi siler."""
        selected_row = self.category_table.currentRow()
        if selected_row < 0:
            return
        
        category_id = self.category_table.item(selected_row, 0).text()
        category_name = self.category_table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(
            self, "Onay",
            f"{category_name} kategorisini silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.data_manager.delete_category(category_id):
                    self.load_categories()
                    self.clear_form()
                    QMessageBox.information(self, "Başarılı", "Kategori başarıyla silindi.")
                else:
                    QMessageBox.warning(self, "Uyarı", "Kategori silinirken bir hata oluştu.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Kategori silinirken bir hata oluştu: {str(e)}") 