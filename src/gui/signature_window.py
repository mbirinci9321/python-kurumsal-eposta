from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QLineEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QDialog,
    QDialogButtonBox, QTextEdit, QSplitter,
    QMessageBox, QToolBar, QStatusBar, QHeaderView,
    QFileDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon
from utils.data_manager import DataManager
from .icons import IconManager
import json
from datetime import datetime

class SignatureDialog(QDialog):
    def __init__(self, parent=None, data_manager=None, signature=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.signature = signature
        
        self.setWindowTitle("Yeni İmza" if not signature else "İmza Düzenle")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Ana düzen
        layout = QVBoxLayout()
        
        # Form düzeni
        form_layout = QFormLayout()
        
        # İmza adı
        self.name_edit = QLineEdit()
        form_layout.addRow("İmza Adı:", self.name_edit)
        
        # Departman seçimi
        self.department_combo = QComboBox()
        self.department_combo.addItem("Tümü", "")
        for dept in self.data_manager.get_departments():
            self.department_combo.addItem(dept, dept)
        form_layout.addRow("Departman:", self.department_combo)
        
        # HTML editör
        self.html_editor = QTextEdit()
        form_layout.addRow("HTML İçerik:", self.html_editor)
        
        # Önizleme alanı
        self.preview_label = QLabel("Önizleme")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid #ccc; padding: 10px;")
        form_layout.addRow("Önizleme:", self.preview_label)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        # Eğer imza düzenleniyorsa, form alanlarını doldur
        if signature:
            self.name_edit.setText(signature.get("name", ""))
            self.department_combo.setCurrentText(signature.get("department", ""))
            self.html_editor.setHtml(signature.get("html_content", ""))
            self.update_preview()
        
        # HTML editör değiştiğinde önizlemeyi güncelle
        self.html_editor.textChanged.connect(self.update_preview)
    
    def update_preview(self):
        """HTML içeriğini önizleme alanında göster"""
        self.preview_label.setText(self.html_editor.toHtml())
    
    def accept(self):
        """Form verilerini doğrula ve kaydet"""
        name = self.name_edit.text().strip()
        department = self.department_combo.currentData()
        html_content = self.html_editor.toHtml()
        
        if not name:
            QMessageBox.warning(self, "Hata", "İmza adı boş olamaz!")
            return
        
        if not html_content:
            QMessageBox.warning(self, "Hata", "HTML içeriği boş olamaz!")
            return
        
        # İmza verilerini hazırla
        signature_data = {
            "name": name,
            "department": department,
            "html_content": html_content,
            "updated_at": datetime.now().isoformat()
        }
        
        if self.signature:
            # Mevcut imzayı güncelle
            signature_data["id"] = self.signature["id"]
            signature_data["created_at"] = self.signature["created_at"]
            self.data_manager.update_signature(signature_data)
        else:
            # Yeni imza ekle
            signature_data["id"] = str(len(self.data_manager.get_signatures()) + 1)
            signature_data["created_at"] = datetime.now().isoformat()
            self.data_manager.add_signature(signature_data)
        
        super().accept()

class SignatureWindow(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager
        self.icon_manager = IconManager()
        
        self.init_ui()
        self.load_signatures()
    
    def init_ui(self):
        """Arayüzü oluşturur."""
        layout = QVBoxLayout()
        
        # Araç çubuğu
        toolbar = QHBoxLayout()
        
        add_button = QPushButton("Yeni İmza")
        add_button.clicked.connect(self.show_add_signature_dialog)
        self.icon_manager.set_icon(add_button, "add")
        toolbar.addWidget(add_button)
        
        edit_button = QPushButton("Düzenle")
        edit_button.clicked.connect(self.show_edit_signature_dialog)
        self.icon_manager.set_icon(edit_button, "edit")
        toolbar.addWidget(edit_button)
        
        delete_button = QPushButton("Sil")
        delete_button.clicked.connect(self.delete_signature)
        self.icon_manager.set_icon(delete_button, "delete")
        toolbar.addWidget(delete_button)
        
        toolbar.addStretch()
        
        # Arama ve filtreleme
        search_label = QLabel("Ara:")
        toolbar.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("İmza ara...")
        self.search_edit.textChanged.connect(self.filter_signatures)
        toolbar.addWidget(self.search_edit)
        
        layout.addLayout(toolbar)
        
        # İmza tablosu
        self.signature_table = QTableWidget()
        self.signature_table.setColumnCount(4)
        self.signature_table.setHorizontalHeaderLabels(["ID", "İmza Adı", "Departman", "Son Güncelleme"])
        self.signature_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.signature_table)
        
        self.setLayout(layout)
    
    def load_signatures(self):
        """İmzaları yükler."""
        self.signature_table.setRowCount(0)
        signatures = self.data_manager.get_signatures()
        
        for signature in signatures:
            row = self.signature_table.rowCount()
            self.signature_table.insertRow(row)
            
            self.signature_table.setItem(row, 0, QTableWidgetItem(signature["id"]))
            self.signature_table.setItem(row, 1, QTableWidgetItem(signature["name"]))
            self.signature_table.setItem(row, 2, QTableWidgetItem(signature["department"]))
            self.signature_table.setItem(row, 3, QTableWidgetItem(
                datetime.fromisoformat(signature["updated_at"]).strftime("%d.%m.%Y %H:%M")
            ))
        
        self.signature_table.resizeColumnsToContents()
    
    def filter_signatures(self):
        """İmzaları filtreler."""
        department = self.department_combo.currentData()
        search_text = self.search_edit.text().lower()
        
        for row in range(self.signature_table.rowCount()):
            show_row = True
            
            # Departman filtresi
            if department and self.signature_table.item(row, 2).text() != department:
                show_row = False
            
            # Arama filtresi
            if search_text and search_text not in self.signature_table.item(row, 1).text().lower():
                show_row = False
            
            self.signature_table.setRowHidden(row, not show_row)
    
    def show_add_signature_dialog(self):
        """Yeni imza ekleme dialogunu gösterir."""
        dialog = SignatureDialog(self, self.data_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_signatures()
    
    def show_edit_signature_dialog(self):
        """İmza düzenleme dialogunu gösterir."""
        selected = self.signature_table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        signature_id = self.signature_table.item(row, 0).text()
        signature = self.data_manager.get_signature_by_id(signature_id)
        
        if signature:
            dialog = SignatureDialog(self, self.data_manager, signature)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_signatures()
    
    def delete_signature(self):
        """Seçili imzayı siler."""
        selected = self.signature_table.selectedItems()
        if not selected:
            return
        
        row = selected[0].row()
        signature_id = self.signature_table.item(row, 0).text()
        signature_name = self.signature_table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "İmza Sil",
            f"{signature_name} imzasını silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.data_manager.delete_signature(signature_id):
                self.load_signatures()
    
    def export_signatures(self):
        """İmzaları dışa aktar"""
        # TODO: İmzaları JSON dosyasına aktar
        pass
    
    def import_signatures(self):
        """İmzaları içe aktar"""
        # TODO: JSON dosyasından imzaları içe aktar
        pass
    
    def bulk_assign_signatures(self):
        """İmzaları toplu olarak kullanıcılara ata"""
        # TODO: Toplu imza atama işlemi
        pass 