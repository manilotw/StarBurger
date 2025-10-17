from .models import Place
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