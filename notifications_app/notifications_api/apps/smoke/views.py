from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class Smoke(GenericAPIView):
    def get(self, request):
        return Response({"msg": "OK"})
