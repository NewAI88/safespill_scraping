import os
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from config import Config

class ExcelHandler:
    def __init__(self, region: str):
        self.region = region
        self.config = Config()
        self.reports_dir = self.config.REPORTS_DIR
        
        # Ensure reports directory exists
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Define filename based on region
        if region == 'uk_na':
            self.filename = 'UK_NA_hangar_projects.xlsx'
        elif region == 'emea':
            self.filename = 'EMEA_hangar_projects.xlsx'
        else:
            self.filename = f'{region}_hangar_projects.xlsx'
        
        self.filepath = os.path.join(self.reports_dir, self.filename)
    
    def create_new_excel(self, data: List[Dict[str, Any]]) -> str:
        """Create a new Excel file with the scraped data"""
        try:
            # Convert data to DataFrame
            df = pd.DataFrame(data)
            
            # Create workbook and worksheet
            wb = Workbook()
            ws = wb.active
            ws.title = "Hangar Projects"
            
            # Add headers
            headers = self.config.EXCEL_FIELDS
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=1, column=col, value=header)
                cell.font = Font(bold=True)
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.font = Font(color="FFFFFF", bold=True)
                cell.alignment = Alignment(horizontal="center")
            
            # Add data rows
            for row_idx, row_data in enumerate(data, 2):
                for col_idx, field in enumerate(headers, 1):
                    value = row_data.get(field, '')
                    cell = ws.cell(row=row_idx, column=col_idx, value=value)
                    
                    # Add hyperlink for Source URL column
                    if field == 'Source URL' and value:
                        cell.hyperlink = value
                        cell.font = Font(color="0000FF", underline="single")
                        cell.value = "Click to open"
            
            # Auto-adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
            
            # Save the workbook
            wb.save(self.filepath)
            
            print(f"Created new Excel file: {self.filepath}")
            return self.filepath
            
        except Exception as e:
            print(f"Error creating Excel file: {str(e)}")
            raise
    
    def update_existing_excel(self, new_data: List[Dict[str, Any]]) -> str:
        """Update existing Excel file by adding new data to the top"""
        try:
            if not os.path.exists(self.filepath):
                return self.create_new_excel(new_data)
            
            # Load existing workbook
            wb = load_workbook(self.filepath)
            ws = wb.active
            
            # Get existing data
            existing_data = []
            headers = self.config.EXCEL_FIELDS
            
            # Read existing data (skip header row)
            for row in ws.iter_rows(min_row=2, values_only=True):
                if any(row):  # Skip empty rows
                    row_dict = dict(zip(headers, row))
                    existing_data.append(row_dict)
            
            # Combine new data with existing data (new data first)
            combined_data = new_data + existing_data
            
            # Clear existing content (except header)
            ws.delete_rows(2, ws.max_row)
            
            # Add combined data
            for row_idx, row_data in enumerate(combined_data, 2):
                for col_idx, field in enumerate(headers, 1):
                    value = row_data.get(field, '')
                    cell = ws.cell(row=row_idx, column=col_idx, value=value)
                    
                    # Add hyperlink for Source URL column
                    if field == 'Source URL' and value:
                        cell.hyperlink = value
                        cell.font = Font(color="0000FF", underline="single")
                        cell.value = "Click to open"
            
            # Save the workbook
            wb.save(self.filepath)
            
            print(f"Updated Excel file: {self.filepath}")
            return self.filepath
            
        except Exception as e:
            print(f"Error updating Excel file: {str(e)}")
            raise
    
    def get_existing_urls(self) -> set:
        """Get existing URLs from the Excel file to avoid duplicates"""
        try:
            if not os.path.exists(self.filepath):
                return set()
            
            wb = load_workbook(self.filepath)
            ws = wb.active
            
            existing_urls = set()
            url_column = self.config.EXCEL_FIELDS.index('Source URL') + 1
            
            # Read URLs from existing data (skip header row)
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row and len(row) >= url_column:
                    url = row[url_column - 1]
                    if url and url != "Click to open":
                        existing_urls.add(url)
            
            return existing_urls
            
        except Exception as e:
            print(f"Error reading existing URLs: {str(e)}")
            return set()
    
    def filter_new_articles(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out articles that already exist in the Excel file"""
        existing_urls = self.get_existing_urls()
        new_articles = []
        
        for article in articles:
            url = article.get('Source URL', '')
            if url and url not in existing_urls:
                new_articles.append(article)
        
        print(f"Found {len(new_articles)} new articles out of {len(articles)} total")
        return new_articles
    
    def get_file_info(self) -> Dict[str, Any]:
        """Get information about the Excel file"""
        try:
            if not os.path.exists(self.filepath):
                return {
                    'exists': False,
                    'filepath': self.filepath,
                    'size': 0,
                    'last_modified': None,
                    'row_count': 0
                }
            
            stat = os.stat(self.filepath)
            
            # Count rows in Excel file
            wb = load_workbook(self.filepath)
            ws = wb.active
            row_count = ws.max_row - 1  # Subtract header row
            
            return {
                'exists': True,
                'filepath': self.filepath,
                'size': stat.st_size,
                'last_modified': datetime.fromtimestamp(stat.st_mtime),
                'row_count': max(0, row_count)
            }
            
        except Exception as e:
            print(f"Error getting file info: {str(e)}")
            return {
                'exists': False,
                'filepath': self.filepath,
                'size': 0,
                'last_modified': None,
                'row_count': 0
            } 