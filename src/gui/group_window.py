from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QDialog, QDialogButtonBox, QFormLayout, QLineEdit,
    QTextEdit, QMessageBox, QHeaderView, QMenu
)
from PyQt6.QtCore import Qt
from utils.data_manager import DataManager

class GroupDialog(QDialog):
    def __init__(self, parent=None, group=None):
        super().__init__(parent)
        self.group = group
        self.setWindowTitle("Yeni Grup" if group is None else "Grubu Düzenle")
        self.setMinimumWidth(400)
        self.setMinimumHeight(200)
        
        layout = QVBoxLayout(self)
        
        # Form alanları
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        if group:
            self.name_edit.setText(group["name"])
        form_layout.addRow("İsim:", self.name_edit)
        
        self.description_edit = QTextEdit()
        if group:
            self.description_edit.setText(group.get("description", ""))
        form_layout.addRow("Açıklama:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_group_data(self):
        return {
            "name": self.name_edit.text(),
            "description": self.description_edit.toPlainText()
        }

class GroupWindow(QMainWindow):
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("Grup Yönetimi")
        self.setMinimumSize(800, 600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        self.main_layout = QVBoxLayout(central_widget)
        
        self.setup_ui()
        self.load_groups()  # Initialize with groups
        
    def setup_ui(self):
        # Üst toolbar
        toolbar = QHBoxLayout()
        
        self.add_button = QPushButton("Yeni Grup")
        self.add_button.clicked.connect(self.show_add_dialog)
        toolbar.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Düzenle")
        self.edit_button.clicked.connect(self.show_edit_dialog)
        toolbar.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Sil")
        self.delete_button.clicked.connect(self.delete_group)
        toolbar.addWidget(self.delete_button)
        
        self.main_layout.addLayout(toolbar)
        
        # Grup tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "İsim", "Açıklama", "Son Güncelleme"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        self.main_layout.addWidget(self.table)
        
    def load_groups(self):
        """Grupları tabloya yükler."""
        groups = self.data_manager.get_all_groups()
        self.table.setRowCount(len(groups))
        
        for row, group in enumerate(groups):
            self.table.setItem(row, 0, QTableWidgetItem(group["id"]))
            self.table.setItem(row, 1, QTableWidgetItem(group["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(group.get("description", "")))
            self.table.setItem(row, 3, QTableWidgetItem(group["updated_at"]))
            
    def show_add_dialog(self):
        """Yeni grup ekleme dialogunu gösterir."""
        dialog = GroupDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_group_data()
            self.data_manager.create_group(
                data["name"],
                data["description"]
            )
            self.load_groups()
            
    def show_edit_dialog(self):
        """Grup düzenleme dialogunu gösterir."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek istediğiniz grubu seçin.")
            return
            
        group_id = self.table.item(selected_row, 0).text()
        group = self.data_manager.get_group_by_id(group_id)
        
        dialog = GroupDialog(self, group)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_group_data()
            self.data_manager.update_group(group_id, {
                **group,
                **data
            })
            self.load_groups()
            
    def delete_group(self):
        """Seçili grubu siler."""
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek istediğiniz grubu seçin.")
            return
            
        group_id = self.table.item(selected_row, 0).text()
        group_name = self.table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(
            self,
            "Onay",
            f"{group_name} grubunu silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.data_manager.delete_group(group_id):
                self.load_groups()
                
    def show_context_menu(self, pos):
        """Bağlam menüsünü gösterir."""
        menu = QMenu()
        
        edit_action = menu.addAction("Düzenle")
        edit_action.triggered.connect(self.show_edit_dialog)
        
        delete_action = menu.addAction("Sil")
        delete_action.triggered.connect(self.delete_group)
        
        menu.exec(self.table.viewport().mapToGlobal(pos)) 