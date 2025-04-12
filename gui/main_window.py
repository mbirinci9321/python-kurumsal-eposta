#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QTabWidget,
    QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("Kurumsal E-posta İmza Yönetim Sistemi")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Hazır")
        
        # Initialize tabs
        self._init_tabs()
        
    def _init_tabs(self):
        # TODO: Initialize different tabs for:
        # - User Management
        # - Signature Templates
        # - License Management
        # - Settings
        pass
        
    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Çıkış",
            "Uygulamadan çıkmak istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore() 