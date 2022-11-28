import requests
from celery import shared_task

from listings.models import AirBnbListing, Outcode


@shared_task
def fetch_outcode_data(listing_id):
    # If we didn't have to worry about postcodes.io rate limits
    # this could possibly be spun out to a celery task in order to improve performance
    listing = AirBnbListing.objects.get(id=listing_id)
    postcode_response = requests.get(
        f"http://api.postcodes.io/postcodes?lon={listing.longitude}&lat={listing.latitude}"
    )
    data = postcode_response.json()
    if data.get("result", None):
        if len(data["result"]) > 0:
            for result in data["result"]:
                outcode, created = Outcode.objects.get_or_create(name=result["outcode"])
                if created or not outcode.latitude:
                    outcode.latitude = result["latitude"]
                    outcode.longitude = result["longitude"]

                if outcode.nearest_codes.count() == 0:
                    fetch_nearby_outcodes(outcode.id)
                listing.outcode = outcode
                listing.save()


def fetch_nearby_outcodes(outcode_id):
    outcode = Outcode.objects.get(id=outcode_id)
    nearest_outcode_response = requests.get(
        f"http://api.postcodes.io/outcodes/{outcode.name}/nearest"
    )
    data = nearest_outcode_response.json()
    if data.get("result", None):
        if len(data["result"]) > 0:
            for result in data["result"]:
                if result["outcode"] != outcode.name:
                    closest_outcode, created = Outcode.objects.get_or_create(
                        name=result["outcode"]
                    )
                    if created or not closest_outcode.latitude:
                        closest_outcode.latitude = result["latitude"]
                        closest_outcode.longitude = result["longitude"]
                        closest_outcode.save()
                    outcode.nearest_codes.add(closest_outcode)
                    outcode.save()
            return
    print(f"No close outcodes for {outcode.name}")
