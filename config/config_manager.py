#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import configparser
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_path = Path("config/config.ini")
        self._load_config()

    def _load_config(self):
        if not self.config_path.exists():
            self._create_default_config()
        self.config.read(self.config_path)

    def _create_default_config(self):
        self.config["AD"] = {
            "server": "ldap://your-ad-server",
            "port": "389",
            "base_dn": "DC=example,DC=com",
            "username": "admin",
            "password": "password"
        }

        self.config["License"] = {
            "key": "",
            "expiry_date": "",
            "status": "inactive"
        }

        self.config["Logging"] = {
            "level": "INFO",
            "file": "logs/app.log"
        }

        # Create config directory if it doesn't exist
        os.makedirs(self.config_path.parent, exist_ok=True)
        
        with open(self.config_path, "w") as f:
            self.config.write(f)

    def get(self, section, key, default=None):
        try:
            return self.config[section][key]
        except (KeyError, configparser.NoSectionError):
            return default

    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self._save_config()

    def _save_config(self):
        with open(self.config_path, "w") as f:
            self.config.write(f) 