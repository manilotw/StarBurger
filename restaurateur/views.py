from django import forms
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.db.models import F, Sum
from geopy import distance
from place.models import Place

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from environs import Env
import requests

from foodcartapp.models import Product, Restaurant, Order
from star_burger.settings import yandex_api_key
from place.utils import fetch_coordinates, get_all_addresses_with_coords

class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    address_to_coords = get_all_addresses_with_coords()

    orders = (
        Order.objects
        .exclude(status='Done')
        .prefetch_related('items__product')
        .order_by('status')
        .with_available_restaurants()
    )

    for order in orders:
        order_coords = address_to_coords.get(order.address)

        if not order_coords:
            order.address_not_found = True
            continue

        order.address_not_found = False

        restaurants_with_distance = []

        for restaurant in order.restaurants:
            restaurant_coords = address_to_coords.get(restaurant.address)

            if restaurant_coords:
                try:
                    
                    rest_point = (float(restaurant_coords[1]), float(restaurant_coords[0]))
                    order_point = (float(order_coords[1]), float(order_coords[0]))
                    dist_km = round(distance.distance(rest_point, order_point).km, 2)
                except Exception:
                    dist_km = "Ошибка определения координат"
            else:
                dist_km = "Ошибка определения координат"

            restaurants_with_distance.append({
                'name': restaurant.name,
                'address': restaurant.address,
                'distance': dist_km,
            })

        order.restaurants = sorted(
            restaurants_with_distance,
            key=lambda r: (r['distance'] if isinstance(r['distance'], (int, float)) else float('inf'), r['name'])
        )

    return render(request, 'order_items.html', {'order_items': orders})