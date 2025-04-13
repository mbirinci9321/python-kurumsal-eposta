from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QDialogButtonBox, QFormLayout, QMessageBox
)
from PyQt6.QtCore import Qt

class TemplateDialog(QDialog):
    def __init__(self, parent=None, data_manager=None, template=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.template = template
        self.setWindowTitle("Yeni Şablon" if not template else "Şablon Düzenle")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Form alanları
        form_layout = QFormLayout()
        
        # Şablon adı
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Şablon adı")
        form_layout.addRow("Ad:", self.name_edit)
        
        # Kategori seçimi
        self.category_combo = QComboBox()
        self.category_combo.addItem("Kategori Seçin", None)
        for category in self.data_manager.get_categories():
            self.category_combo.addItem(category["name"], category["id"])
        form_layout.addRow("Kategori:", self.category_combo)
        
        # Açıklama
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Şablon açıklaması")
        self.description_edit.setMaximumHeight(100)
        form_layout.addRow("Açıklama:", self.description_edit)
        
        # İçerik
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Şablon içeriği (HTML)")
        form_layout.addRow("İçerik:", self.content_edit)
        
        # Durum
        self.active_check = QCheckBox("Aktif")
        self.active_check.setChecked(True)
        form_layout.addRow("Durum:", self.active_check)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Eğer şablon düzenleniyorsa, form alanlarını doldur
        if self.template:
            self.name_edit.setText(self.template.get("name", ""))
            self.description_edit.setText(self.template.get("description", ""))
            self.content_edit.setText(self.template.get("content", ""))
            self.active_check.setChecked(self.template.get("is_active", True))
            
            # Kategori seçimi
            category_id = self.template.get("category_id")
            if category_id:
                index = self.category_combo.findData(category_id)
                if index >= 0:
                    self.category_combo.setCurrentIndex(index)

    def accept(self):
        """Form verilerini doğrular ve kabul eder."""
        name = self.name_edit.text().strip()
        content = self.content_edit.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Uyarı", "Şablon adı boş olamaz!")
            return
        
        if not content:
            QMessageBox.warning(self, "Uyarı", "Şablon içeriği boş olamaz!")
            return
        
        try:
            if self.template:
                # Şablon güncelleme
                self.data_manager.update_template(
                    self.template["id"],
                    name=name,
                    content=content,
                    description=self.description_edit.toPlainText().strip(),
                    category_id=self.category_combo.currentData(),
                    is_active=self.active_check.isChecked()
                )
            else:
                # Yeni şablon ekleme
                self.data_manager.add_template(
                    name=name,
                    content=content,
                    description=self.description_edit.toPlainText().strip(),
                    category_id=self.category_combo.currentData(),
                    is_active=self.active_check.isChecked()
                )
            super().accept()
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Şablon kaydedilirken bir hata oluştu: {str(e)}") 