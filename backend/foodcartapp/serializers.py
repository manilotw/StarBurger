from rest_framework.serializers import ModelSerializer, ValidationError
from phonenumber_field.validators import validate_international_phonenumber

from .models import Order, OrderItem


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
