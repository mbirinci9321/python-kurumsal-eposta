import os
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QMenu

class IconManager:
    """İkon yönetimi sınıfı."""
    
    def __init__(self):
        self.icon_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons")
        self.icons = {}
        self.load_icons()
    
    def load_icons(self):
        """İkonları yükler."""
        if not os.path.exists(self.icon_dir):
            os.makedirs(self.icon_dir)
            
        for icon_name in [
            "add", "backup", "delete", "edit", "export",
            "file", "filter", "import", "quit", "refresh",
            "save", "search", "settings", "warning"
        ]:
            icon_path = os.path.join(self.icon_dir, f"{icon_name}.png")
            if os.path.exists(icon_path):
                self.icons[icon_name] = QIcon(icon_path)
    
    def set_icon(self, target, icon_name: str):
        """Hedefe ikon atar."""
        if icon_name in self.icons:
            if isinstance(target, QAction):
                target.setIcon(self.icons[icon_name])
            elif isinstance(target, QMenu):
                target.setIcon(self.icons[icon_name])
    
    def get_icon(self, icon_name: str) -> QIcon:
        """İkon döndürür."""
        return self.icons.get(icon_name, QIcon())

# Global icon manager instance
icon_manager = IconManager()

__all__ = ["IconManager", "set_icon"] 