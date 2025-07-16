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
            self.filename = 'UK_NA.xlsx'
        elif region == 'emea':
            self.filename = 'EMEA.xlsx'
        else:
            self.filename = f'{region}.xlsx'

        self.filepath = os.path.join(self.reports_dir, self.filename)
    
    def create_new_excel(self) -> str:
        """Create a new Excel file with the scraped data"""
        try:
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
            
            # # Add data rows
            # for row_idx, row_data in enumerate(data, 2):
            #     for col_idx, field in enumerate(headers, 1):
            #         value = row_data.get(field, '')
            #         cell = ws.cell(row=row_idx, column=col_idx, value=value)
                    
            #         # Add hyperlink for Source URL column
            #         if field == 'Source URL' and value:
            #             cell.hyperlink = value
            #             cell.font = Font(color="0000FF", underline="single")
            #             cell.value = value
            
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
        max_retries = 3
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                if not os.path.exists(self.filepath):
                    self.create_new_excel()
                
                # Load existing workbook
                wb = load_workbook(self.filepath)
                ws = wb.active
                
                # Get existing data
                existing_data = []
                headers = self.config.EXCEL_FIELDS
                
                # Key (first word of title + region + country)
                keys = []
                
                # Read existing data (skip header row)
                for row in ws.iter_rows(min_row=2, values_only=True):
                    if any(row):  # Skip empty rows
                        row_dict = dict(zip(headers, row))
                        existing_data.append(row_dict)
                        keys.append(f"{row_dict.get('Title', '').split()[0].lower()}_{row_dict.get('Region', '').lower()}_{row_dict.get('Country', '').lower()}")
                
                # Filter new data to avoid duplicates
                filtered_new_data = []
                for article in new_data:
                    title = article.get('Title', '').split()[0].lower()
                    region = article.get('Region', '').lower()
                    country = article.get('Country', '').lower()
                    key = f"{title}_{region}_{country}"
                    
                    if key not in keys:
                        filtered_new_data.append(article)
                        keys.append(key)
                
                # Combine new data with existing data (new data first)
                combined_data = filtered_new_data + existing_data

                # Clear existing content (except header)
                ws.delete_rows(2, ws.max_row)
                
                # # Define fills
                # red_fill = PatternFill(start_color="fa0228", end_color="fa0228", fill_type="solid")
                # blue_fill = PatternFill(start_color="00f7ff", end_color="00f7ff", fill_type="solid")
                # yellow_fill = PatternFill(start_color="ffe100", end_color="ffe100", fill_type="solid")
                
                # Add combined data
                for row_idx, row_data in enumerate(combined_data, 2):
                    for col_idx, field in enumerate(headers, 1):
                        value = row_data.get(field, '')
                        cell = ws.cell(row=row_idx, column=col_idx, value=value)
                        
                        # Add hyperlink for Source URL column
                        if field == 'Source URL' and value:
                            cell.hyperlink = value
                            cell.font = Font(color="0000FF", underline="single")
                            cell.value = value
                    
                #     # 🔻 Apply background color based on conditions
                #     if row_data.get("Region") != self.region.upper():
                #         ws[f"A{row_idx}"].fill = red_fill
                #         ws[f"E{row_idx}"].fill = red_fill
                #     elif not row_data.get("Is Hangar Related", False):
                #         ws[f"A{row_idx}"].fill = yellow_fill
                #         ws[f"G{row_idx}"].fill = yellow_fill
                #     elif row_data.get("Completion Status", False):
                #         ws[f"A{row_idx}"].fill = blue_fill
                #         ws[f"H{row_idx}"].fill = blue_fill
                
                # Save the workbook
                wb.save(self.filepath)
                
                print(f"Updated Excel file: {self.filepath}")
                return self.filepath, len(filtered_new_data)
                
            except PermissionError as e:
                if attempt < max_retries - 1:
                    print(f"Permission denied on attempt {attempt + 1}. File may be open in another application.")
                    print(f"Please close the Excel file '{self.filename}' and retrying in {retry_delay} seconds...")
                    import time
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print(f"Error updating Excel file after {max_retries} attempts: {str(e)}")
                    print(f"Please ensure the file '{self.filename}' is not open in Excel or another application.")
                    raise
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
                    if url:
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