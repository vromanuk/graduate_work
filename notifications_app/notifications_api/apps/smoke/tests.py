import http

from django.urls import reverse


def test_smoke(client):
    url = reverse("smoke")
    response = client.get(url, format="json")
    response_json = response.json()
    assert response.status_code == http.HTTPStatus.OK
    assert response_json == {"msg": "OK"}
