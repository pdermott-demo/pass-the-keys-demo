import csv
from datetime import datetime

import requests
from django.core.management.base import BaseCommand

from listings.models import AirBnbListing, Outcode
from listings.tasks import fetch_outcode_data


def process_csv_row(row_data):
    created = False
    if "id" in row_data:
        if "last_review" in row_data and row_data["last_review"] != "":
            row_data["last_review"] = datetime.strptime(
                row_data["last_review"], "%Y-%m-%d"
            )
        else:
            row_data["last_review"] = None
            row_data["reviews_per_month"] = None
        try:
            listing = AirBnbListing.objects.get(air_bnb_id=row_data["id"])
        except AirBnbListing.DoesNotExist:
            listing = AirBnbListing.objects.create(
                **row_data, air_bnb_id=row_data["id"]
            )
            created = True

    if created:
        fetch_outcode_data.delay(listing_id=listing.id)


class Command(BaseCommand):
    help = "Fetches the listing data from airbnb and populate outcodes"

    def handle(self, *args, **options):
        AirBnbListing.objects.all().delete()
        Outcode.objects.all().delete()

        file_url = "http://data.insideairbnb.com/united-kingdom/england/greater-manchester/2021-10-24/visualisations/listings.csv"
        response = requests.get(file_url)
        open("airbnb.csv", "wb").write(response.content)

        with open("airbnb.csv", encoding="utf8") as csv_file:
            rows = csv.DictReader(csv_file, delimiter=",")
            i = 0
            for row in rows:
                i += 1
                print(f"Processing listing {i}")
                process_csv_row(row)

        print(
            "Import complete, celery tasks to fetch outcode data may still be running"
        )
