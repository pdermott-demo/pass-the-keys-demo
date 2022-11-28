from django.db import models
from geopy.distance import geodesic


# Create your models here.
class AirBnbListing(models.Model):
    air_bnb_id = models.PositiveIntegerField()
    name = models.CharField(max_length=1024)
    host_id = models.PositiveIntegerField()  # Could be a ForeignKey in a real app
    host_name = models.CharField(max_length=1024)
    neighbourhood_group = models.CharField(max_length=255)
    neighbourhood = models.CharField(max_length=255)
    room_type = models.CharField(max_length=255)
    price = models.PositiveIntegerField()
    minimum_nights = models.PositiveIntegerField()
    number_of_reviews = models.PositiveIntegerField()
    number_of_reviews_ltm = models.PositiveIntegerField()
    last_review = models.DateField(blank=True, null=True)
    reviews_per_month = models.FloatField(blank=True, null=True)
    calculated_host_listings_count = models.PositiveIntegerField()
    availability_365 = models.PositiveIntegerField()
    license = models.CharField(max_length=255, blank=True, null=True)

    # If we needed to do more than the task we wish to look at using a PointField
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    outcode = models.ForeignKey(
        "Outcode",
        blank=True,
        null=True,
        related_name="listings",
        on_delete=models.SET_NULL,
    )


class Outcode(models.Model):
    name = models.CharField(max_length=4, blank=True, unique=True)
    nearest_codes = models.ManyToManyField("self", symmetrical=False, related_name="+")
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def get_average_daily_price(self):
        total_price = 0
        if self.listings.count() > 0:
            for listing in self.listings.all():
                total_price += listing.price
            return round(total_price / self.listings.count(), 2)
        return 0

    def get_distance_from_nexus(self, origin):
        if origin:
            return round(
                geodesic(
                    (origin.latitude, origin.longitude), (self.latitude, self.longitude)
                ).miles,
                3,
            )
        return 0
