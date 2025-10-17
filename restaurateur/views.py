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

def fetch_coordinates(apikey, address):
    try:
        place = Place.objects.filter(address_place=address).first()
        if place and place.lon and place.lat:
            return place.lon, place.lat
        else:
            base_url = "https://geocode-maps.yandex.ru/1.x"
            response = requests.get(base_url, params={
                "geocode": address,
                "apikey": apikey,
                "format": "json",
            })
            response.raise_for_status()
            found_places = response.json()['response']['GeoObjectCollection']['featureMember']

            if not found_places:
                return None

            most_relevant = found_places[0]
            lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
            return lon, lat
    except (requests.RequestException, KeyError, IndexError):
        return None

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
    
    orders = (
    Order.objects
    .exclude(status='Done')
    .prefetch_related('items__product')
    .with_available_restaurants()
    .order_by('status')
)

    for order in orders:
        order_coords = fetch_coordinates(yandex_api_key, order.address)

        if not order_coords:
            order.address_not_found = True
            continue

        order.address_not_found = False

        for restaurant in order.restaurants:
            restaurant_coords = fetch_coordinates(yandex_api_key, restaurant.address)
            if restaurant_coords:
                restaurant.distance = round(distance.distance(restaurant_coords[::-1], order_coords[::-1]).km, 2)
            else:
                restaurant.distance = "Ошибка определения координат"

        order.restaurants = sorted(
            order.restaurants,
            key=lambda r: r.distance if isinstance(r.distance, (int, float)) else float('inf')
        )

    return render(request, 'order_items.html', {'order_items': orders})
