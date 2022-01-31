from django.urls import include, path

urlpatterns = [path("v1/", include("subscriptions.api.v1.urls"))]
