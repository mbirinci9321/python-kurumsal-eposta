from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QComboBox, QLineEdit, QFormLayout, QMessageBox,
    QTextEdit, QDialog, QDialogButtonBox, QCheckBox,
    QToolBar, QFileDialog, QHeaderView, QMenu
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, pyqtSignal
from utils.data_manager import DataManager
import json
from datetime import datetime
from gui.icons import icon_manager

class TemplateDialog(QDialog):
    """Şablon ekleme/düzenleme dialogu."""
    
    def __init__(self, parent=None, data_manager=None, template=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.template = template
        
        self.setWindowTitle("Yeni Şablon" if not template else "Şablon Düzenle")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Ana düzen
        layout = QVBoxLayout()
        
        # Form düzeni
        form_layout = QFormLayout()
        
        # Şablon adı
        self.name_edit = QLineEdit()
        form_layout.addRow("Şablon Adı:", self.name_edit)
        
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
        
        # Eğer şablon düzenleniyorsa, form alanlarını doldur
        if template:
            self.name_edit.setText(template.get("name", ""))
            self.department_combo.setCurrentText(template.get("department", ""))
            self.html_editor.setHtml(template.get("html_content", ""))
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
            QMessageBox.warning(self, "Hata", "Şablon adı boş olamaz!")
            return
        
        if not html_content:
            QMessageBox.warning(self, "Hata", "HTML içeriği boş olamaz!")
            return
        
        # Şablon verilerini hazırla
        template_data = {
            "name": name,
            "department": department,
            "html_content": html_content,
            "updated_at": datetime.now().isoformat()
        }
        
        if self.template:
            # Mevcut şablonu güncelle
            template_data["id"] = self.template["id"]
            template_data["created_at"] = self.template["created_at"]
            self.data_manager.update_template(template_data)
        else:
            # Yeni şablon ekle
            template_data["id"] = str(len(self.data_manager.get_templates()) + 1)
            template_data["created_at"] = datetime.now().isoformat()
            self.data_manager.add_template(template_data)
        
        super().accept()

class TemplateWindow(QWidget):
    """Şablon yönetimi penceresi."""
    
    def __init__(self, data_manager, icon_manager):
        super().__init__()
        self.data_manager = data_manager
        self.icon_manager = icon_manager
        
        # Ana layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
        # Araç çubuğunu oluştur
        self.create_toolbar()
        
        # Filtreleme alanını oluştur
        self.create_filter_area()
        
        # Şablon tablosunu oluştur
        self.create_template_table()
        
        # Alt araç çubuğunu oluştur
        self.create_bottom_toolbar()
        
        # Şablonları yükle
        self.load_templates()
    
    def create_toolbar(self):
        """Araç çubuğunu oluşturur."""
        toolbar = QToolBar()
        
        # Yeni şablon ekle butonu
        add_action = QAction("Yeni Şablon", self)
        self.icon_manager.set_icon(add_action, "template_add")
        add_action.triggered.connect(self.show_new_template_dialog)
        toolbar.addAction(add_action)
        
        # Şablon düzenle butonu
        edit_action = QAction("Şablon Düzenle", self)
        self.icon_manager.set_icon(edit_action, "template_edit")
        edit_action.triggered.connect(self.show_edit_template_dialog)
        toolbar.addAction(edit_action)
        
        # Şablon sil butonu
        delete_action = QAction("Şablon Sil", self)
        self.icon_manager.set_icon(delete_action, "template_delete")
        delete_action.triggered.connect(self.delete_template)
        toolbar.addAction(delete_action)
        
        toolbar.addSeparator()
        
        # Dışa aktarma butonu
        export_action = QAction("Dışa Aktar", self)
        self.icon_manager.set_icon(export_action, "export")
        export_action.triggered.connect(self.export_templates)
        toolbar.addAction(export_action)
        
        # İçe aktarma butonu
        import_action = QAction("İçe Aktar", self)
        self.icon_manager.set_icon(import_action, "import")
        import_action.triggered.connect(self.import_templates)
        toolbar.addAction(import_action)
        
        self.main_layout.addWidget(toolbar)
    
    def create_filter_area(self):
        """Filtreleme alanını oluşturur."""
        filter_widget = QWidget()
        filter_layout = QHBoxLayout()
        
        # Departman filtresi
        self.department_combo = QComboBox()
        self.department_combo.addItem("Tüm Departmanlar", "")
        for dept in self.data_manager.get_departments():
            self.department_combo.addItem(dept, dept)
        self.department_combo.currentIndexChanged.connect(self.filter_templates)
        filter_layout.addWidget(QLabel("Departman:"))
        filter_layout.addWidget(self.department_combo)
        
        # Arama kutusu
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Şablon ara...")
        self.search_edit.textChanged.connect(self.filter_templates)
        filter_layout.addWidget(QLabel("Ara:"))
        filter_layout.addWidget(self.search_edit)
        
        filter_widget.setLayout(filter_layout)
        self.main_layout.addWidget(filter_widget)
    
    def create_template_table(self):
        """Şablon tablosunu oluşturur."""
        self.template_table = QTableWidget()
        self.template_table.setColumnCount(4)
        self.template_table.setHorizontalHeaderLabels(["ID", "Ad", "Açıklama", "Son Güncelleme"])
        self.template_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.template_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.template_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.template_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.template_table.customContextMenuRequested.connect(self.show_context_menu)
        self.template_table.setSortingEnabled(True)
        self.main_layout.addWidget(self.template_table)
    
    def create_bottom_toolbar(self):
        """Alt araç çubuğunu oluşturur."""
        bottom_toolbar = QToolBar()
        
        # Durum etiketi
        self.status_label = QLabel("Toplam 0 şablon")
        bottom_toolbar.addWidget(self.status_label)
        
        bottom_toolbar.addSeparator()
        
        # Yenile butonu
        refresh_action = QAction("Yenile", self)
        self.icon_manager.set_icon(refresh_action, "refresh")
        refresh_action.triggered.connect(self.load_templates)
        bottom_toolbar.addAction(refresh_action)
        
        self.main_layout.addWidget(bottom_toolbar)
    
    def load_templates(self):
        """Şablonları yükler ve tabloyu günceller."""
        # Departman listesini güncelle
        departments = self.data_manager.get_departments()
        self.department_combo.clear()
        self.department_combo.addItem("Tümü")
        self.department_combo.addItems(departments)
        
        # Şablonları yükle
        templates = self.data_manager.get_templates()
        self.template_table.setRowCount(len(templates))
        
        for row, template in enumerate(templates):
            self.template_table.setItem(row, 0, QTableWidgetItem(str(template["id"])))
            self.template_table.setItem(row, 1, QTableWidgetItem(template["name"]))
            self.template_table.setItem(row, 2, QTableWidgetItem(template["department"]))
            self.template_table.setItem(row, 3, QTableWidgetItem(template["updated_at"]))
        
        self.template_table.resizeColumnsToContents()
        self.status_label.setText(f"Toplam {len(templates)} şablon")
    
    def filter_templates(self):
        """Şablonları filtreler ve tabloya ekler."""
        department = self.department_combo.currentText()
        search_text = self.search_edit.text().lower()
        
        # Tüm şablonları al
        templates = self.data_manager.get_templates()
        
        # Departman filtresi
        if department != "Tümü":
            templates = [t for t in templates if t["department"] == department]
        
        # Arama filtresi
        if search_text:
            templates = [
                t for t in templates
                if search_text in t["name"].lower()
            ]
        
        # Tabloyu güncelle
        self.template_table.setRowCount(len(templates))
        for row, template in enumerate(templates):
            self.template_table.setItem(row, 0, QTableWidgetItem(str(template["id"])))
            self.template_table.setItem(row, 1, QTableWidgetItem(template["name"]))
            self.template_table.setItem(row, 2, QTableWidgetItem(template["department"]))
            self.template_table.setItem(row, 3, QTableWidgetItem(template["updated_at"]))
        
        # Sütun genişliklerini ayarla
        self.template_table.resizeColumnsToContents()
        
        # Durum etiketini güncelle
        self.status_label.setText(f"Toplam {len(templates)} şablon")
    
    def show_new_template_dialog(self):
        """Yeni şablon ekleme penceresini gösterir."""
        dialog = TemplateDialog(self, self.data_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_templates()
    
    def show_edit_template_dialog(self):
        """Şablon düzenleme dialogunu gösterir."""
        selected_items = self.template_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir şablon seçin.")
            return
        
        template_id = int(self.template_table.item(selected_items[0].row(), 0).text())
        template = self.data_manager.get_template_by_id(template_id)
        
        if template:
            dialog = TemplateDialog(self, self.data_manager, template)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_templates()
    
    def delete_template(self):
        """Seçili şablonu siler."""
        selected_row = self.template_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek istediğiniz şablonu seçin.")
            return
        
        template_id = self.template_table.item(selected_row, 0).text()
        template = self.data_manager.get_template_by_id(template_id)
        
        if not template:
            QMessageBox.warning(self, "Uyarı", "Seçili şablon bulunamadı.")
            return
        
        reply = QMessageBox.question(
            self, "Onay",
            f"{template.get('name', 'Bilinmeyen Şablon')} şablonunu silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.data_manager.delete_template(template_id)
                self.load_templates()
                QMessageBox.information(self, "Başarılı", "Şablon başarıyla silindi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Şablon silinirken bir hata oluştu: {str(e)}")
    
    def export_templates(self):
        """Şablonları dışa aktarır."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Şablonları Dışa Aktar",
            "",
            "JSON Dosyaları (*.json)"
        )
        
        if file_path:
            try:
                templates = self.data_manager.get_templates()
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(templates, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "Bilgi", "Şablonlar başarıyla dışa aktarıldı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dışa aktarma sırasında hata oluştu: {str(e)}")
    
    def import_templates(self):
        """Şablonları içe aktarır."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Şablonları İçe Aktar",
            "",
            "JSON Dosyaları (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    templates = json.load(f)
                    for template in templates:
                        self.data_manager.add_template(template)
                self.load_templates()
                QMessageBox.information(self, "Bilgi", "Şablonlar başarıyla içe aktarıldı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"İçe aktarma sırasında hata oluştu: {str(e)}")
    
    def show_context_menu(self, pos):
        """Bağlam menüsünü gösterir"""
        menu = QMenu()
        
        edit_action = QAction("Düzenle", self)
        edit_action.triggered.connect(self.show_edit_template_dialog)
        self.icon_manager.set_icon(edit_action, "edit")
        menu.addAction(edit_action)
        
        delete_action = QAction("Sil", self)
        delete_action.triggered.connect(self.delete_template)
        self.icon_manager.set_icon(delete_action, "delete")
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # Sütun gizleme/gösterme
        column_menu = menu.addMenu("Sütunlar")
        for i in range(self.template_table.columnCount()):
            action = QAction(self.template_table.horizontalHeaderItem(i).text(), self)
            action.setCheckable(True)
            action.setChecked(not self.template_table.isColumnHidden(i))
            action.triggered.connect(lambda checked, col=i: self.template_table.setColumnHidden(col, not checked))
            column_menu.addAction(action)
        
        menu.exec_(self.template_table.viewport().mapToGlobal(pos)) 