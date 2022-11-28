from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from rest_framework.views import APIView

from listings.models import Outcode


class OutcodeView(APIView):
    def get(self, request, outcode_str):
        outcode = get_object_or_404(Outcode, name=outcode_str.upper())

        context = {"outcode": outcode}
        return TemplateResponse(
            request, "api/outcode.xml", context, content_type="application/xml"
        )


class NexusOutcodeView(APIView):
    def get(self, request, outcode_str):
        outcode = get_object_or_404(Outcode, name=outcode_str.upper())
        close_code_list = []

        for close_code in outcode.nearest_codes.all():
            avg_price = close_code.get_average_daily_price()
            distance = close_code.get_distance_from_nexus(outcode)
            close_code_list.append(
                {
                    "name": close_code.name,
                    "listing_count": close_code.listings.count(),
                    "avg_price": avg_price,
                    "distance": distance,
                }
            )

        context = {
            "outcode": outcode,
            "close_codes": close_code_list,
        }

        return TemplateResponse(
            request, "api/nexus.xml", context, content_type="application/xml"
        )
