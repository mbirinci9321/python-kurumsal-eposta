from datetime import datetime
import json
import csv
from typing import List, Dict, Any
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import pandas as pd

class ReportManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.report_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)

    def generate_user_activity_report(self, start_date: str = None, end_date: str = None, output_format: str = "pdf") -> str:
        """Kullanıcı aktivite raporu oluşturur"""
        users = self.data_manager.get_users()
        report_data = []
        
        for user in users:
            user_data = {
                "Kullanıcı ID": user["id"],
                "Ad Soyad": user["full_name"],
                "E-posta": user["email"],
                "Departman": user["department"],
                "Rol": user["role"],
                "Durum": user["status"],
                "Son Giriş": user.get("last_login", "Bilinmiyor"),
                "Oluşturulma Tarihi": user["created_at"]
            }
            report_data.append(user_data)
        
        return self._save_report("user_activity", report_data, output_format)

    def generate_license_usage_report(self, start_date: str = None, end_date: str = None, output_format: str = "pdf") -> str:
        """Lisans kullanım raporu oluşturur"""
        licenses = self.data_manager.get_licenses()
        report_data = []
        
        for license in licenses:
            license_data = {
                "Lisans ID": license["id"],
                "Lisans Anahtarı": license["key"],
                "Tip": license["type"],
                "Başlangıç Tarihi": license["start_date"],
                "Bitiş Tarihi": license["end_date"],
                "Durum": license["status"],
                "Kullanıcı ID": license["user_id"],
                "Oluşturulma Tarihi": license["created_at"]
            }
            report_data.append(license_data)
        
        return self._save_report("license_usage", report_data, output_format)

    def generate_template_statistics(self, start_date: str = None, end_date: str = None, output_format: str = "pdf") -> str:
        """Şablon kullanım istatistikleri oluşturur"""
        templates = self.data_manager.get_templates()
        report_data = []
        
        for template in templates:
            template_data = {
                "Şablon ID": template["id"],
                "Ad": template["name"],
                "Departman": template["department"],
                "Durum": template["status"],
                "Kullanım Sayısı": template.get("usage_count", 0),
                "Son Kullanım": template.get("last_used", "Bilinmiyor"),
                "Oluşturulma Tarihi": template["created_at"]
            }
            report_data.append(template_data)
        
        return self._save_report("template_statistics", report_data, output_format)

    def _save_report(self, report_type: str, data: List[Dict[str, Any]], output_format: str) -> str:
        """Raporu belirtilen formatta kaydeder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_{timestamp}.{output_format}"
        filepath = os.path.join(self.report_dir, filename)
        
        if output_format == "pdf":
            self._save_as_pdf(filepath, data)
        elif output_format == "excel":
            self._save_as_excel(filepath, data)
        elif output_format == "csv":
            self._save_as_csv(filepath, data)
        elif output_format == "json":
            self._save_as_json(filepath, data)
        
        return filepath

    def _save_as_pdf(self, filepath: str, data: List[Dict[str, Any]]):
        """Raporu PDF formatında kaydeder"""
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        
        # Başlık
        styles = getSampleStyleSheet()
        title = Paragraph("Rapor", styles["Title"])
        elements.append(title)
        
        # Tablo verilerini hazırla
        if data:
            headers = list(data[0].keys())
            table_data = [headers]
            for row in data:
                table_data.append([str(row[header]) for header in headers])
            
            # Tablo oluştur
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        
        doc.build(elements)

    def _save_as_excel(self, filepath: str, data: List[Dict[str, Any]]):
        """Raporu Excel formatında kaydeder"""
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)

    def _save_as_csv(self, filepath: str, data: List[Dict[str, Any]]):
        """Raporu CSV formatında kaydeder"""
        if data:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

    def _save_as_json(self, filepath: str, data: List[Dict[str, Any]]):
        """Raporu JSON formatında kaydeder"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4) 