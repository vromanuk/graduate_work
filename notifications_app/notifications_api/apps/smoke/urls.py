from django.urls import path

from notifications_api.apps.smoke import views

urlpatterns = [
    path("smoke/", views.Smoke.as_view(), name="smoke"),
]
