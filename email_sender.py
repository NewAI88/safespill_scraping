import os
import base64
from datetime import datetime
from mailjet_rest import Client
from dotenv import load_dotenv
import glob
import random

load_dotenv()  # Load from .env

class EmailSender:
    def __init__(self):
        self.api_key = os.getenv('MJ_APIKEY_PUBLIC')
        self.api_secret = os.getenv('MJ_APIKEY_PRIVATE')
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.mailjet = Client(auth=(self.api_key, self.api_secret), version='v3.1')
    
    def send_report_email(self, filepath: str, region: str, article_count: int, recipient_email: str) -> bool:
        try:
            if not all([self.api_key, self.api_secret, self.sender_email, recipient_email]):
                print("Mailjet configuration incomplete.")
                return False

            current_date = datetime.now().strftime('%B %d, %Y')
            subject = self._get_subject(region)
            html_body = self._create_email_body(region, article_count, current_date)

            attachment_data = self._get_attachment_base64(filepath)
            if not attachment_data:
                return False

            data = {
                'Messages': [{
                    "From": {
                        "Email": self.sender_email,
                        "Name": "Safespill Reports"
                    },
                    "To": [{
                        "Email": recipient_email,
                        "Name": "Safespill Team"
                    }],
                    "Subject": subject,
                    "HTMLPart": html_body,
                    "Attachments": [{
                        "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "Filename": os.path.basename(filepath),
                        "Base64Content": attachment_data
                    }]
                }]
            }

            result = self.mailjet.send.create(data=data)
            if result.status_code == 200:
                print("✅ Email sent successfully.")
                return True
            else:
                print(f"❌ Failed to send email: {result.status_code}")
                print(result.json())
                return False

        except Exception as e:
            print(f"Error sending report: {e}")
            return False

    def _get_subject(self, region: str) -> str:
        if region == 'uk_na':
            return "Safespill - UK & North America Hangar Projects Report"
        elif region == 'emea':
            return "Safespill - EMEA Hangar Projects Report"
        else:
            return f"Safespill - {region.upper()} Hangar Projects Report"

    def _create_email_body(self, region: str, article_count: int, current_date: str) -> str:
        region_name = {
            'uk_na': 'UK & North America',
            'emea': 'EMEA (Europe, Middle East, Africa)'
        }.get(region, region.upper())

        return f"""
        <h2>Safespill Weekly Report - {region_name}</h2>
        <p>Date: {current_date}</p>
        <p>New articles found: {article_count}</p>
        <p>Please find the attached report.</p>
        """

    def _get_attachment_base64(self, filepath: str) -> str:
        if not os.path.isfile(filepath):
            print(f"❌ Attachment not found: {filepath}")
            return None
        with open(filepath, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def test_send(self):
        reports_dir = './reports/'
        files = [f for f in os.listdir(reports_dir) if f.endswith('.xlsx')]
        if not files:
            print("❌ No report files found in './reports/'")
            return False
        
        chosen_file = random.choice(files)
        filepath = os.path.join(reports_dir, chosen_file)
        
        # Determine region from filename
        if chosen_file.lower().startswith('uk_na'):
            region = 'uk_na'
        elif chosen_file.lower().startswith('emea'):
            region = 'emea'
        else:
            region = 'unknown'
        
        # Fake article count for test
        article_count = random.randint(5, 15)
        
        print(f"Sending test email with file: {chosen_file}, region: {region}, article_count: {article_count}")
        return self.send_report_email(filepath, region, article_count)
