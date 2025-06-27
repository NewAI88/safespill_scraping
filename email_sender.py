import smtplib
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List
from config import Config

class EmailSender:
    def __init__(self):
        self.config = Config()
        self.smtp_server = self.config.SMTP_SERVER
        self.smtp_port = self.config.SMTP_PORT
        self.email_user = self.config.EMAIL_USER
        self.email_password = self.config.EMAIL_PASSWORD
        self.recipient_emails = self.config.RECIPIENT_EMAILS
    
    def send_report_email(self, filepath: str, region: str, article_count: int) -> bool:
        """Send Excel report via email"""
        try:
            if not all([self.email_user, self.email_password, self.recipient_emails]):
                print("Email configuration incomplete. Skipping email send.")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = ', '.join(self.recipient_emails)
            
            # Set subject based on region
            if region == 'uk_na':
                subject = "Safespill - UK & North America Hangar Projects Report"
            elif region == 'emea':
                subject = "Safespill - EMEA Hangar Projects Report"
            else:
                subject = f"Safespill - {region.upper()} Hangar Projects Report"
            
            msg['Subject'] = subject
            
            # Create email body
            current_date = datetime.now().strftime('%B %d, %Y')
            body = self._create_email_body(region, article_count, current_date)
            msg.attach(MIMEText(body, 'html'))
            
            # Attach Excel file
            if os.path.exists(filepath):
                self._attach_file(msg, filepath)
            else:
                print(f"Excel file not found: {filepath}")
                return False
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                text = msg.as_string()
                server.sendmail(self.email_user, self.recipient_emails, text)
            
            print(f"Email sent successfully to {len(self.recipient_emails)} recipients")
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def _create_email_body(self, region: str, article_count: int, current_date: str) -> str:
        """Create HTML email body"""
        region_name = {
            'uk_na': 'UK & North America',
            'emea': 'EMEA (Europe, Middle East, Africa)'
        }.get(region, region.upper())
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #366092; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .footer {{ background-color: #f4f4f4; padding: 15px; text-align: center; font-size: 12px; }}
                .highlight {{ background-color: #fff2cc; padding: 10px; border-left: 4px solid #ffc107; }}
                .stats {{ background-color: #e8f4fd; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Safespill Hangar Projects Report</h1>
                <h2>{region_name}</h2>
                <p>Weekly MRO Hangar Construction & Retrofit Projects</p>
            </div>
            
            <div class="content">
                <p>Dear Safespill Sales Team,</p>
                
                <p>Please find attached the weekly report of aircraft Maintenance, Repair, and Overhaul (MRO) 
                hangar construction and retrofit projects for the <strong>{region_name}</strong> region.</p>
                
                <div class="stats">
                    <h3>📊 Report Summary</h3>
                    <ul>
                        <li><strong>Report Date:</strong> {current_date}</li>
                        <li><strong>Region:</strong> {region_name}</li>
                        <li><strong>New Articles Found:</strong> {article_count}</li>
                        <li><strong>Sources:</strong> Google News & Bing News</li>
                    </ul>
                </div>
                
                <div class="highlight">
                    <h3>🔍 What's Included</h3>
                    <p>This report contains news articles about:</p>
                    <ul>
                        <li>Aircraft MRO hangar construction projects</li>
                        <li>Maintenance facility expansions and renovations</li>
                        <li>Hangar retrofit and modernization projects</li>
                        <li>Aviation maintenance facility developments</li>
                    </ul>
                    <p><em>Note: Articles about museums, historic aircraft, air shows, and unrelated aviation content have been filtered out.</em></p>
                </div>
                
                <h3>📋 Excel Report Details</h3>
                <p>The attached Excel file contains the following information for each project:</p>
                <ul>
                    <li><strong>Project Title:</strong> Name or description of the hangar project</li>
                    <li><strong>Source URL:</strong> Direct link to the news article (clickable hyperlink)</li>
                    <li><strong>Summary:</strong> Brief description of the project</li>
                    <li><strong>Country/Region:</strong> Specific country or region where the project is located</li>
                    <li><strong>Language:</strong> Language of the source article</li>
                    <li><strong>Date Published:</strong> When the article was published</li>
                    <li><strong>Week Collected:</strong> When this information was gathered</li>
                </ul>
                
                <p>This information is designed to support your sales efforts by identifying potential customers 
                and market opportunities in the aircraft hangar construction and retrofit sector.</p>
                
                <p>Best regards,<br>
                Safespill Automated Reporting System</p>
            </div>
            
            <div class="footer">
                <p>This is an automated report generated by Safespill's news monitoring system.<br>
                For questions or technical support, please contact your IT department.</p>
            </div>
        </body>
        </html>
        """
        
        return html_body
    
    def _attach_file(self, msg: MIMEMultipart, filepath: str):
        """Attach Excel file to email"""
        try:
            with open(filepath, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            
            # Add header for file attachment
            filename = os.path.basename(filepath)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            
            msg.attach(part)
            print(f"Attached file: {filename}")
            
        except Exception as e:
            print(f"Error attaching file: {str(e)}")
    
    def test_email_configuration(self) -> bool:
        """Test email configuration"""
        try:
            if not all([self.email_user, self.email_password, self.smtp_server]):
                print("Email configuration incomplete")
                return False
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                print("Email configuration test successful")
                return True
                
        except Exception as e:
            print(f"Email configuration test failed: {str(e)}")
            return False 