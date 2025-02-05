from django.core.management.base import BaseCommand
from Ebay.cron_daily import eBayScraper  # Import your eBayScraper class

class Command(BaseCommand):
    help = 'Update eBay data periodically'

    def handle(self, *args, **options):
        scraper = eBayScraper()  # Initialize your eBayScraper
        scraper.handle()  # Call the handle method to perform the scraping and database updates
