from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QTextEdit, QLineEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QFrame, QDialog, QFormLayout,
                             QToolBar)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QIcon, QAction
from .icons import IconManager
import sys
import os

# Ana proje dizinini Python modül yoluna ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.signature_manager import SignatureManager
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SignatureWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("İmza Yönetimi")
        self.setMinimumSize(800, 600)
        
        # Get DataManager from parent
        main_window = self.parent()
        if main_window and hasattr(main_window, 'data_manager'):
            self.data_manager = main_window.data_manager
        else:
            from src.utils.data_manager import DataManager
            self.data_manager = DataManager()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        self.main_layout = QVBoxLayout(central_widget)
        
        self.signature_manager = SignatureManager(self.data_manager)
        self.setup_ui()
        self.load_signatures()  # Initialize with signatures
        
    def setup_ui(self):
        # Create toolbar
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Add actions
        add_action = QAction("Ekle", self)
        add_action.triggered.connect(self.show_add_dialog)
        toolbar.addAction(add_action)
        
        edit_action = QAction("Düzenle", self)
        edit_action.triggered.connect(self.show_edit_dialog)
        toolbar.addAction(edit_action)
        
        delete_action = QAction("Sil", self)
        delete_action.triggered.connect(self.delete_template)
        toolbar.addAction(delete_action)
        
        push_action = QAction("Gönder", self)
        push_action.triggered.connect(self.push_signatures)
        toolbar.addAction(push_action)
        
        # Create table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "İsim", "Açıklama", "Son Güncelleme"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.main_layout.addWidget(self.table)

    def load_signatures(self):
        """İmza şablonlarını yükler ve tabloya ekler"""
        try:
            # Mevcut tablo içeriğini temizle
            self.table.setRowCount(0)
            
            # Tüm şablonları al
            templates = self.signature_manager.get_all_signature_templates()
            
            # Tabloyu doldur
            for template in templates:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # ID
                id_item = QTableWidgetItem(str(template.get('id', '')))
                self.table.setItem(row, 0, id_item)
                
                # İsim
                name_item = QTableWidgetItem(template.get('name', ''))
                self.table.setItem(row, 1, name_item)
                
                # Açıklama
                desc_item = QTableWidgetItem(template.get('description', ''))
                self.table.setItem(row, 2, desc_item)
                
                # Son güncelleme
                last_updated = template.get('last_updated', '')
                if last_updated:
                    last_updated = datetime.fromtimestamp(last_updated).strftime('%Y-%m-%d %H:%M:%S')
                update_item = QTableWidgetItem(last_updated)
                self.table.setItem(row, 3, update_item)
            
            self.table.resizeColumnsToContents()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İmza şablonları yüklenirken hata oluştu: {str(e)}")
            logger.log_error("İmza şablonları yüklenirken hata", {"error": str(e)})

    def refresh_signatures(self):
        """İmza listesini yeniler"""
        self.load_signatures()

    def show_add_dialog(self):
        """Yeni şablon ekleme dialogunu gösterir."""
        dialog = SignatureDialog(self.signature_manager, parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_signatures()

    def show_edit_dialog(self):
        """Şablon düzenleme dialogunu gösterir."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlenecek şablonu seçin.")
            return

        row = selected[0].row()
        template_id = self.table.item(row, 0).text()
        template = self.signature_manager.get_signature_template(template_id)
        
        if template:
            dialog = SignatureDialog(self.signature_manager, template=template, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_signatures()
        else:
            QMessageBox.warning(self, "Uyarı", f"Şablon bulunamadı (ID: {template_id}).")

    def delete_template(self):
        """Seçili şablonu siler."""
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek şablonu seçin.")
            return

        row = selected[0].row()
        template_id = self.table.item(row, 0).text()
        template_name = self.table.item(row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Onay",
            f"{template_name} şablonunu silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.signature_manager.delete_signature_template(template_id):
                self.load_signatures()
                QMessageBox.information(self, "Başarılı", "Şablon başarıyla silindi.")
            else:
                QMessageBox.critical(self, "Hata", "Şablon silinirken bir hata oluştu.")

    def push_signatures(self):
        """İmzaları gruplara uygular."""
        reply = QMessageBox.question(
            self,
            "Onay",
            "Seçili imza şablonlarını gruplara uygulamak istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                result = self.signature_manager.push_signatures_to_groups()
                
                if result.get('success', []):
                    success_count = len(result['success'])
                    failed_count = len(result.get('failed', []))
                    
                    message = f"İmzalar başarıyla uygulandı.\n"
                    message += f"Başarılı: {success_count} grup\n"
                    if failed_count > 0:
                        message += f"Başarısız: {failed_count} grup"
                    
                    QMessageBox.information(self, "Başarılı", message)
                else:
                    error_message = "İmzalar uygulanırken hata oluştu."
                    if result.get('failed'):
                        error_details = [f"{err.get('error', 'Bilinmeyen hata')}" 
                                      for err in result['failed']]
                        error_message += "\n\nHatalar:\n" + "\n".join(error_details)
                    
                    QMessageBox.critical(self, "Hata", error_message)
                    
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Hata",
                    f"İmzalar uygulanırken beklenmeyen bir hata oluştu:\n{str(e)}"
                )

class SignatureDialog(QDialog):
    def __init__(self, signature_manager, template=None, parent=None):
        super().__init__(parent)
        self.signature_manager = signature_manager
        self.template = template
        self.setWindowTitle("İmza Şablonu Ekle" if not template else "İmza Şablonu Düzenle")
        self.init_ui()
    
    def init_ui(self):
        """Dialog arayüzünü oluşturur."""
        self.setMinimumWidth(600)
        
        layout = QFormLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # İsim alanı
        self.name_input = QLineEdit()
        if self.template:
            self.name_input.setText(self.template['name'])
            self.name_input.setEnabled(False)
        layout.addRow("Şablon Adı:", self.name_input)
        
        # Açıklama alanı
        self.description_input = QLineEdit()
        if self.template:
            self.description_input.setText(self.template['description'])
        layout.addRow("Açıklama:", self.description_input)
        
        # İçerik alanı
        self.content_input = QTextEdit()
        self.content_input.setMinimumHeight(300)
        if self.template:
            self.content_input.setHtml(self.template['content'])
        layout.addRow("İçerik:", self.content_input)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        save_button = QPushButton('Kaydet')
        save_button.clicked.connect(self.accept)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #388E3C;
            }
        """)
        
        cancel_button = QPushButton('İptal')
        cancel_button.clicked.connect(self.reject)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #757575;
            }
        """)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        layout.addRow("", button_layout)

    def accept(self):
        """Dialog kabul edildiğinde çağrılır."""
        try:
            template_data = self.get_template_data()
            
            if not template_data["name"]:
                QMessageBox.warning(self, "Uyarı", "Lütfen şablon adını girin.")
                return
                
            if not template_data["content"]:
                QMessageBox.warning(self, "Uyarı", "Lütfen şablon içeriğini girin.")
                return
                
            if self.template:
                # Şablonu güncelle
                success = self.signature_manager.update_signature_template(
                    self.template["id"],
                    template_data["name"],
                    template_data["description"],
                    template_data["content"]
                )
            else:
                # Yeni şablon oluştur
                success = self.signature_manager.create_signature_template(
                    template_data["name"],
                    template_data["description"],
                    template_data["content"]
                )
                
            if success:
                super().accept()
            else:
                QMessageBox.critical(self, "Hata", "Şablon kaydedilemedi.")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İşlem sırasında bir hata oluştu:\n{str(e)}")
    
    def get_template_data(self):
        """Dialog verilerini döndürür."""
        return {
            'name': self.name_input.text(),
            'description': self.description_input.text(),
            'content': self.content_input.toHtml()
        } 