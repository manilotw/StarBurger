from django.http import JsonResponse
from django.templatetags.static import static
import json

from .models import Product, Order, OrderItem
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from phonenumber_field.validators import validate_international_phonenumber


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })

@api_view(['POST'])
def register_order(request):
    # TODO это лишь заглушка


    print('request.body:', request.data)
    data = request.data
    print('Получены данные:', data)
    try:
        if not data['products'] or not isinstance(data['products'], list):
            return Response({'err': 'it is mt or not list'})
        fields = ['firstname', 'lastname', 'address', 'phonenumber']
        for field in fields:
            if not data[field]:
                return Response({'Ifelse': 'pls fill out all'})
        for index in range(4):
            field = fields[index]
            if not isinstance(data[field], str):
                return Response({'NotStr': 'Go fill like str'})
        try:
            validate_international_phonenumber(data['phonenumber'])
        except ValidationError:
            return Response({'Phonenumber': 'Ur phone is not valid'})
        
            

        order = Order.objects.create(
            firstname = data['firstname'],
            lastname = data['lastname'],
            phonenumber = data['phonenumber'],
            address = data['address']
            )
          
        for item in data['products']:
            try:
                product = Product.objects.get(id=item['product'])
            except:
                return Response({'Product': 'Invalid id of product'})
            OrderItem.objects.create(order=order, product=product, quantity=item['quantity'])
        return Response({'ok': 'add'})
    except KeyError:
        return Response({'Error': 'Br i think u no have product'})
    
    
