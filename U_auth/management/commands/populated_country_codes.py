from django.core.management.base import BaseCommand
from U_auth.models import Country_codes
import phonenumbers
import pycountry

class Command(BaseCommand):
    help = 'Populates the Country_codes model with country calling codes'

    def handle(self, *args, **kwargs):
        for region in phonenumbers.SUPPORTED_REGIONS:
            calling_code = phonenumbers.country_code_for_region(region)
            
            # Get the country name using the ISO country code from pycountry
            try:
                country_name = pycountry.countries.get(alpha_2=region).name
            except AttributeError:
                country_name = 'Unknown'
            
            # Check for existing records before creating
            existing_record = Country_codes.objects.filter(country_name=country_name).first()
            if existing_record:
                self.stdout.write(self.style.WARNING(f"Duplicate country name found: {country_name}. Skipping..."))
                continue
            
            existing_record = Country_codes.objects.filter(calling_code=f"+{calling_code}").first()
            if existing_record:
                self.stdout.write(self.style.WARNING(f"Duplicate calling code found: {calling_code}. Skipping..."))
                continue

            Country_codes.objects.create(
                country_name=country_name,
                calling_code=f"+{calling_code}"
            )
            
        self.stdout.write(self.style.SUCCESS('Successfully populated Country_codes model'))