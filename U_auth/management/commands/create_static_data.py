import time
from typing import Any
from django.core.management.base import BaseCommand
from U_auth.models import Interests, Hobbies, LifestyleChoice, Qualifications, Disabilities


data_list = [(Qualifications, 'qualification', ('Bachelor', 'Master', 'PhD', 'Diploma', 'Associate')), 
             (Interests, 'interest' ,('Technology', 'Sports', 'Arts', 'Science', 'Movies', 'Music', 'Fitness')),
             (Hobbies, 'hobby' ,('Reading', 'Traveling', 'Cooking', 'Gardening', 'Music', 'Photography')), 
             (LifestyleChoice, 'name', ('Healthy', 'Sedentary', 'Active', 'Moderate')),
             (Disabilities, 'disability_type', ('Hearing', 'Visual', 'Mobility', 'Cognitive', 'None'))
            ]

starting_time = time.time()
class Command(BaseCommand):
    help = 'This will create some data in your db such as (Interests, Hobbies, LifestyleChoice, Qualifications, Disabilities)'

    def handle(self, *args: Any, **options: Any) -> str | None:
        for model in data_list:
            model_class, field_name, items = model
            for item in items:
                # Dynamically create a filter with field_name
                if model_class.objects.filter(**{field_name: item}).exists():
                    self.stdout.write(self.style.WARNING(f"{model_class.__name__} '{item}' already exists skipping..!!!"))
                    # continue
                else:
                    # Dynamically create the object
                    model_class.objects.create(**{field_name: item})
                    self.stdout.write(self.style.SUCCESS(f"Created {model_class.__name__} '{item}'"))

        self.stdout.write(self.style.SUCCESS('Successfully created data in your db'))

ending_time = time.time()
print(f"Time taken to run the command: {ending_time - starting_time} seconds")