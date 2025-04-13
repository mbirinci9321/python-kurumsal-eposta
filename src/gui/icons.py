import os
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QMenu, QPushButton
import base64
from io import BytesIO
from PIL import Image

class IconManager:
    """İkon yönetimi sınıfı."""
    
    def __init__(self):
        self.icons_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
        os.makedirs(self.icons_dir, exist_ok=True)
        self.icons = {}
    
    def load_icons(self):
        """İkonları yükler."""
        if not os.path.exists(self.icons_dir):
            os.makedirs(self.icons_dir)
            
        for icon_name in [
            "add", "backup", "delete", "edit", "export",
            "file", "filter", "import", "quit", "refresh",
            "save", "search", "settings", "warning", "statistics",
            "batch", "group", "license", "user", "user_add",
            "user_edit", "user_delete", "bulk_activate", "bulk_deactivate",
            "bulk_delete", "folder", "cancel", "info", "security",
            "users", "upload", "maximize", "minimize", "restore",
            "help", "about", "print", "view", "preview",
            "template", "assign", "close", "error"
        ]:
            icon_path = os.path.join(self.icons_dir, f"{icon_name}.png")
            if os.path.exists(icon_path):
                self.icons[icon_name] = QIcon(icon_path)
    
    def set_icon(self, target, icon_name: str):
        """Hedefe ikon atar."""
        if icon_name in self.icons:
            if isinstance(target, (QPushButton, QAction)):
                target.setIcon(self.icons[icon_name])
            elif isinstance(target, QMenu):
                target.setIcon(self.icons[icon_name])
    
    def get_icon(self, icon_name: str) -> QIcon:
        """İkon döndürür."""
        return self.icons.get(icon_name, QIcon())

# Global icon manager instance
icon_manager = IconManager()

__all__ = ["IconManager", "set_icon"] 