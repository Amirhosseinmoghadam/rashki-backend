import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from base.models import Province, City

# Static filename expected in the same directory as this command
JSON_FILENAME = "iran_locations.json"


class Command(BaseCommand):
    help = f'Populates Provinces and Cities from "{JSON_FILENAME}" located in the same directory as the command.'

    @transaction.atomic
    def handle(self, *args, **options):
        # Determine the path to the JSON file relative to this command file
        command_dir = os.path.dirname(__file__)
        file_path = os.path.join(command_dir, JSON_FILENAME)

        if not os.path.exists(file_path):
            raise CommandError(
                f'Error: JSON file not found at "{file_path}". '
                f'Please ensure "{JSON_FILENAME}" is in the same directory as populate_locations.py.'
            )

        self.stdout.write(f"Reading location data from: {file_path}")

        # Load and parse JSON data
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            raise CommandError(
                f'Error: Could not decode JSON from file "{file_path}". Ensure it is valid JSON.'
            )
        except Exception as e:
            raise CommandError(f'Error reading file "{file_path}": {e}')

        if not isinstance(data, list):
            raise CommandError("Error: JSON data should be a list of objects.")

        # --- Data Processing Logic ---
        provinces_in_db = {}  # Map: {json_province_id: province_db_object}
        province_count = 0
        city_count = 0
        skipped_provinces = 0
        skipped_cities = 0

        # First Pass: Create Provinces
        self.stdout.write("Processing provinces...")
        for item in data:
            if item.get("type") == "province":
                province_name = item.get("name")  # Use 'name' from JSON
                province_json_id = item.get("id")

                if not province_name:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipping province entry due to missing "name": {item}'
                        )
                    )
                    continue

                # Use 'name' for get_or_create, matching the model field
                province_obj, created = Province.objects.get_or_create(
                    name=province_name
                )

                if created:
                    province_count += 1
                else:
                    skipped_provinces += 1

                if province_json_id:
                    provinces_in_db[province_json_id] = province_obj
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Province "{province_name}" missing "id" in JSON.'
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Finished processing provinces. Created: {province_count}, Skipped: {skipped_provinces}"
            )
        )

        # Second Pass: Create Cities
        self.stdout.write("Processing cities...")
        for item in data:
            if item.get("type") == "county":
                city_name = item.get("name")  # Use 'name' from JSON
                province_ref_id = item.get("province_id")

                if not city_name or province_ref_id is None:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipping city entry due to missing "name" or "province_id": {item}'
                        )
                    )
                    continue

                province_obj = provinces_in_db.get(province_ref_id)
                if not province_obj:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Skipping city "{city_name}". Corresponding province with JSON id "{province_ref_id}" not found.'
                        )
                    )
                    continue

                # Use 'name' for get_or_create, matching the model field
                city_obj, created = City.objects.get_or_create(
                    province=province_obj, name=city_name
                )

                if created:
                    city_count += 1
                else:
                    skipped_cities += 1

        # Final summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\nPopulation process finished.\n"
                f"Provinces processed (created/existing): {province_count + skipped_provinces}\n"
                f"Cities processed (created/existing): {city_count + skipped_cities}"
            )
        )
