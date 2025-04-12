from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtGui import QKeySequence, QShortcut

class ShortcutManager:
    """Kısayol yönetimi sınıfı."""
    
    def __init__(self, window: QMainWindow):
        self.window = window
        self.shortcuts = {}
        self.create_shortcuts()
    
    def create_shortcuts(self):
        """Kısayolları oluşturur."""
        self.add_shortcut("Ctrl+S", self.window.save_data)
        self.add_shortcut("F5", self.window.refresh_all)
        self.add_shortcut("Ctrl+N", lambda: self.window.add_item())
        self.add_shortcut("Ctrl+E", lambda: self.window.edit_item())
        self.add_shortcut("Delete", lambda: self.window.delete_item())
    
    def add_shortcut(self, key: str, callback):
        """Yeni kısayol ekler."""
        shortcut = QShortcut(QKeySequence(key), self.window)
        shortcut.activated.connect(callback)
        self.shortcuts[key] = shortcut 