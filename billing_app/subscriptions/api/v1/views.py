from django.http import JsonResponse
from djstripe.models import Product


def products(request):
    return JsonResponse(
        {
            product.name: [price.human_readable_price for price in product.prices.all()]
            for product in Product.objects.filter(active=True)
        }
    )
