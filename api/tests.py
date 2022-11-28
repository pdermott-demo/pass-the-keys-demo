from django.urls import reverse
from rest_framework.test import APITestCase

from listings.models import Outcode


class OutcodeViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.outcode = Outcode.objects.create(
            name="M7", longitude=-2.26274918556701, latitude=53.5055027912371
        )
        cls.related_outcode = Outcode.objects.create(
            name="M8", longitude=-2.24013769326683, latitude=53.5086869276808
        )
        cls.outcode.nearest_codes.add(cls.related_outcode)
        cls.outcode.save()

        cls.regular_outcode_view_url = reverse(
            "api:outcode", kwargs={"outcode_str": "M7"}
        )

    def test_200_correct_data_with_outcode_view(self):
        response = self.client.get(self.regular_outcode_view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.outcode.name)
        self.assertNotContains(response, self.related_outcode.name)

    def test_404_invalid_outcode(self):
        invalid_outcode_url = reverse("api:outcode", kwargs={"outcode_str": "1234"})
        response = self.client.get(invalid_outcode_url)
        self.assertEqual(response.status_code, 404)


class NexusOutcodeViewTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.outcode = Outcode.objects.create(
            name="M7", longitude=-2.26274918556701, latitude=53.5055027912371
        )
        cls.related_outcode = Outcode.objects.create(
            name="M8", longitude=-2.24013769326683, latitude=53.5086869276808
        )
        cls.outcode.nearest_codes.add(cls.related_outcode)
        cls.outcode.save()

        cls.nexus_outcode_view_url = reverse("api:nexus", kwargs={"outcode_str": "M7"})

    def test_200_correct_data_with_nexus_view(self):
        response = self.client.get(self.nexus_outcode_view_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.outcode.name)
        self.assertContains(response, self.related_outcode.name)

    def test_404_invalid_nexus_outcode(self):
        invalid_nexus_url = reverse("api:outcode", kwargs={"outcode_str": "1234"})
        response = self.client.get(invalid_nexus_url)
        self.assertEqual(response.status_code, 404)
