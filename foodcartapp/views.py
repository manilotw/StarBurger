from django.http import JsonResponse
from django.templatetags.static import static
import json

from .models import Product, Order, OrderItem
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.exceptions import ValidationError as VE
from phonenumber_field.validators import validate_international_phonenumber
from rest_framework.serializers import Serializer, ModelSerializer, CharField, ValidationError, ListField


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

class OrderItemSerializer(ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

class OrderSerializer(ModelSerializer):
    products = OrderItemSerializer(many=True, allow_empty=False, write_only=True)
    class Meta:
        model = Order
        fields = ['products', 'firstname', 'lastname', 'phonenumber', 'address']
        
    
    def validate_phonenumber(self, value):
        try:
            validate_international_phonenumber(value)
        except ValidationError:
            raise ValidationError("Invalid phone number format")
        return value
    
        
print(repr(OrderSerializer()))
    # def validate_products(self, value):
    #     if not isinstance(value, list):
    #         raise ValidationError("Products must be a non-empty list")
    #     return value

# def validate(data):

    # serializer = OrderSerializer(data=data)

    # serializer.is_valid(raise_exception=True)

    # errors = []

    # if not data['products'] or not isinstance(data['products'], list):
    #     errors.append({'err': 'it is mt or not list'})
    # else:
    #     for item in data.get('products', []):
    #         try:
    #             Product.objects.get(id=item['product'])
    #         except Product.DoesNotExist:
    #             errors.append({'Product': f"Invalid id: {item.get('product')}"})

    # fields = ['firstname', 'lastname', 'address', 'phonenumber']
    # for field in fields:
    #     if field not in data or not data[field]:
    #         errors.append({'Ifelse': f'{field} is required'})
    #     elif not isinstance(data[field], str):
    #         errors.append({'NotStr': f'{field} must be str'})

    # try:
    #     validate_international_phonenumber(data.get('phonenumber', ''))
    # except VE:
    #     errors.append({'Phonenumber': 'Ur phone is not valid'})


    # if errors:
    #     raise ValidationError(errors)


@api_view(['POST'])
def register_order(request):
    
    # validate(request.data)
    print('request.body:', request.data)
    
    serializer = OrderSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    print('Получены данные:', data)

    order = Order.objects.create(
        firstname=data['firstname'],
        lastname=data['lastname'],
        phonenumber=data['phonenumber'],
        address=data['address'],
    )

    for item in data['products']:
        product = item['product']
        product = Product.objects.get(id=product.id)
        OrderItem.objects.create(order=order, product=product, quantity=item['quantity'], price=product.price)

    return Response(OrderSerializer(order).data)


    
    
