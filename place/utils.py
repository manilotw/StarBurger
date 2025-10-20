from .models import Place
from star_burger.settings import yandex_api_key
from foodcartapp.models import Order, Restaurant
import requests

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
    
def get_all_addresses_with_coords():
    order_addresses = Order.objects.values_list('address', flat=True)
    restaurant_addresses = Restaurant.objects.values_list('address', flat=True)
    all_addresses = set(order_addresses) | set(restaurant_addresses)

    existing_places = Place.objects.filter(address_place__in=all_addresses)
    address_to_coords = {
        place.address_place: (place.lon, place.lat)
        for place in existing_places
        if place.lon and place.lat
    }

    missing_addresses = [addr for addr in all_addresses if addr not in address_to_coords]

    for address in missing_addresses:
        coords = fetch_coordinates(yandex_api_key, address)
        if coords is None:
            print(f"Адрес не найден: {address}")
            continue

        lon, lat = coords
        Place.objects.create(address_place=address, lon=lon, lat=lat)
        address_to_coords[address] = (lon, lat)

    return address_to_coords