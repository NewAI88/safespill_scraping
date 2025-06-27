import schedule
import time
import logging
from datetime import datetime
from typing import Callable
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingScheduler:
    def __init__(self):
        self.config = Config()
        self.schedule_time = self.config.SCHEDULE_TIME
        self.schedule_day = self.config.SCHEDULE_DAY
    
    def schedule_weekly_run(self, scraping_function: Callable):
        """Schedule the scraping function to run weekly"""
        try:
            # Schedule for Monday at 8:00 AM CT
            if self.schedule_day.lower() == 'monday':
                schedule.every().monday.at(self.schedule_time).do(scraping_function)
            elif self.schedule_day.lower() == 'tuesday':
                schedule.every().tuesday.at(self.schedule_time).do(scraping_function)
            elif self.schedule_day.lower() == 'wednesday':
                schedule.every().wednesday.at(self.schedule_time).do(scraping_function)
            elif self.schedule_day.lower() == 'thursday':
                schedule.every().thursday.at(self.schedule_time).do(scraping_function)
            elif self.schedule_day.lower() == 'friday':
                schedule.every().friday.at(self.schedule_time).do(scraping_function)
            elif self.schedule_day.lower() == 'saturday':
                schedule.every().saturday.at(self.schedule_time).do(scraping_function)
            elif self.schedule_day.lower() == 'sunday':
                schedule.every().sunday.at(self.schedule_time).do(scraping_function)
            else:
                # Default to Monday
                schedule.every().monday.at(self.schedule_time).do(scraping_function)
            
            logger.info(f"Scheduled scraping to run every {self.schedule_day} at {self.schedule_time}")
            
        except Exception as e:
            logger.error(f"Error scheduling scraping: {str(e)}")
    
    def run_scheduler(self):
        """Run the scheduler loop"""
        logger.info("Starting scheduler...")
        logger.info(f"Next run scheduled for {self.schedule_day} at {self.schedule_time}")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
    
    def run_immediately(self, scraping_function: Callable):
        """Run the scraping function immediately"""
        logger.info("Running scraping immediately...")
        try:
            scraping_function()
            logger.info("Immediate scraping completed")
        except Exception as e:
            logger.error(f"Error in immediate scraping: {str(e)}")
    
    def get_next_run_time(self) -> str:
        """Get the next scheduled run time"""
        try:
            # This is a simplified version - in practice, you'd need to calculate
            # the actual next run time based on the current time
            return f"Next {self.schedule_day} at {self.schedule_time}"
        except Exception as e:
            logger.error(f"Error getting next run time: {str(e)}")
            return "Unknown"
    
    def list_scheduled_jobs(self):
        """List all scheduled jobs"""
        try:
            jobs = schedule.get_jobs()
            if jobs:
                logger.info("Scheduled jobs:")
                for job in jobs:
                    logger.info(f"  - {job}")
            else:
                logger.info("No jobs scheduled")
        except Exception as e:
            logger.error(f"Error listing scheduled jobs: {str(e)}") 