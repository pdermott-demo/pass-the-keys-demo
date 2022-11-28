from django.urls import path

from api import views

app_name = "api"

urlpatterns = [
    path("outcode/<str:outcode_str>/", views.OutcodeView.as_view(), name="outcode"),
    path("nexus/<str:outcode_str>/", views.NexusOutcodeView.as_view(), name="nexus"),
]
