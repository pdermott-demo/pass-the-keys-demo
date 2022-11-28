from datetime import date
from unittest import mock

import requests
from django.test import TestCase, override_settings

from listings.management.commands.fetch_data_from_airbnb import (
    process_csv_row,
)
from listings.models import AirBnbListing, Outcode
from listings.tasks import fetch_nearby_outcodes, fetch_outcode_data


class OutcodeModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.airbnb_listing = AirBnbListing.objects.create(
            air_bnb_id=12345,
            name="Test Listing",
            host_id=54321,
            host_name="Test Host",
            neighbourhood_group="Salford",
            neighbourhood="Salford District",
            room_type="Entire home",
            price=41,
            minimum_nights=2,
            number_of_reviews=2,
            number_of_reviews_ltm=0,
            last_review=date(year=2019, month=12, day=8),
            reviews_per_month=1.5,
            availability_365=298,
            calculated_host_listings_count=1,
            license="",
            latitude="53.50114",
            longitude="-2.26429",
        )
        cls.second_listing = AirBnbListing.objects.create(
            air_bnb_id=283495,
            name="En-suite room in detached house",
            host_id=1476718,
            host_name="Alison",
            neighbourhood_group="Rochdale",
            neighbourhood="Rochdale District",
            latitude=53.56259,
            longitude=-2.21945,
            room_type="Private room",
            price=60,
            minimum_nights=3,
            number_of_reviews=10,
            last_review=date(year=2018, month=8, day=5),
            reviews_per_month=0.13,
            calculated_host_listings_count=1,
            availability_365=338,
            number_of_reviews_ltm=0,
            license="",
        )
        cls.outcode = Outcode.objects.create(
            name="M2", longitude=-2.244445, latitude=53.480432
        )
        cls.airbnb_listing.outcode = cls.outcode
        cls.airbnb_listing.save()

        cls.second_listing.outcode = cls.outcode
        cls.second_listing.save()

        cls.related_outcode = Outcode.objects.create(
            name="M8", longitude=-2.24013769326683, latitude=53.5086869276808
        )
        cls.outcode.nearest_codes.add(cls.related_outcode)
        cls.outcode.save()

    def test_get_average_daily_price(self):
        self.assertEqual(self.outcode.get_average_daily_price(), 50.5)

    def test_get_distance_from_nexus(self):
        self.assertEqual(
            self.related_outcode.get_distance_from_nexus(self.outcode), 1.962
        )


@override_settings(CELERY_ALWAYS_EAGER=True)
class FetchDataFromAirBnBTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.row_data = {
            "id": "157612",
            "name": "New attic space/single & Dble room",
            "host_id": "757016",
            "host_name": "Margaret",
            "neighbourhood_group": "Salford",
            "neighbourhood": "Salford District",
            "latitude": "53.50114",
            "longitude": "-2.26429",
            "room_type": "Entire home/apt",
            "price": "41",
            "minimum_nights": "2",
            "number_of_reviews": "96",
            "last_review": "2019-12-08",
            "reviews_per_month": "1.50",
            "calculated_host_listings_count": "1",
            "availability_365": "298",
            "number_of_reviews_ltm": "0",
            "license": "",
        }
        cls.airbnb_listing = AirBnbListing.objects.create(
            air_bnb_id=12345,
            name="Test Listing",
            host_id=54321,
            host_name="Test Host",
            neighbourhood_group="Salford",
            neighbourhood="Salford District",
            room_type="Entire home",
            price=41,
            minimum_nights=2,
            number_of_reviews=2,
            number_of_reviews_ltm=0,
            last_review=date(year=2019, month=1, day=1),
            reviews_per_month=1.5,
            availability_365=298,
            calculated_host_listings_count=1,
            license="",
            latitude=53.50114,
            longitude=-2.26429,
        )
        cls.outcode = Outcode.objects.create(
            name="M2", longitude=-2.244445, latitude=53.480432
        )

    @mock.patch(
        "listings.management.commands.fetch_data_from_airbnb.fetch_outcode_data.delay"
    )
    def test_process_csv_row_will_create_airbnb_listing_object(
        self, mock_fetch_outcode_data
    ):
        initial_count = AirBnbListing.objects.count()
        process_csv_row(self.row_data)
        new_listing = AirBnbListing.objects.get(air_bnb_id=157612)

        self.assertEqual(AirBnbListing.objects.count(), initial_count + 1)
        self.assertEqual(
            new_listing.last_review,
            date(year=2019, month=12, day=8),
        )
        mock_fetch_outcode_data.assert_called_once()

    @mock.patch(
        "listings.management.commands.fetch_data_from_airbnb.fetch_outcode_data.delay"
    )
    def test_process_csv_row_handles_empty_reviews_data(self, mock_fetch_outcode_data):
        initial_count = AirBnbListing.objects.count()
        self.row_data["number_of_reviews"] = 0
        self.row_data["last_review"] = ""
        self.row_data["reviews_per_month"] = ""

        process_csv_row(self.row_data)

        self.assertEqual(AirBnbListing.objects.count(), initial_count + 1)
        mock_fetch_outcode_data.assert_called_once()

    @mock.patch("listings.tasks.fetch_nearby_outcodes")
    def test_fetch_outcode_data_will_create_outcode_object(
        self, mock_fetch_nearby_outcodes
    ):
        initial_outcode_count = Outcode.objects.count()
        fetch_outcode_data(self.airbnb_listing.id)

        self.assertEqual(Outcode.objects.count(), initial_outcode_count + 1)
        self.assertTrue(Outcode.objects.get(name="M2"))
        mock_fetch_nearby_outcodes.assert_called()

    def test_fetch_nearby_outcodes_will_create_additional_outcodes(self):
        initial_outcode_count = Outcode.objects.count()
        fetch_nearby_outcodes(self.outcode.id)

        self.assertNotEqual(Outcode.objects.count(), initial_outcode_count)
        self.assertNotEqual(self.outcode.nearest_codes.count(), 0)
