import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("Missing GOOGLE_MAPS_API_KEY")

def geocode_address(address):
    """
    Uses Google Geocoding API to turn an address string into (lat, lng).
    """
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": address, "key": GOOGLE_API_KEY}
    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return None
    data = resp.json()
    if data.get("status") != "OK":
        return None
    loc = data["results"][0]["geometry"]["location"]
    return loc["lat"], loc["lng"]

def get_user_location_by_ip(ip_address=None):
    """
    Lookup approximate lat/lng for a given IP (or 'me' if None) via ipinfo.io.
    Returns (lat, lng) tuple or None on failure.
    """
    ip = ip_address or 'me'
    try:
        resp = requests.get(f"https://ipinfo.io/{ip}/json")
        if resp.status_code != 200:
            return None
        data = resp.json()
        loc = data.get("loc")  # e.g. "37.3860,-122.0838"
        if not loc:
            return None
        lat_str, lng_str = loc.split(",")
        return float(lat_str), float(lng_str)
    except Exception:
        return None

def get_distance_via_google(orig, dest, unit='km'):
    """
    orig, dest: (lat, lng)
    unit: 'km' or 'mi'
    Returns travel distance (meters→km/mi) or None on failure.
    """
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins":      f"{orig[0]},{orig[1]}",
        "destinations": f"{dest[0]},{dest[1]}",
        "key":          GOOGLE_API_KEY,
        "units":        'imperial' if unit=='mi' else 'metric'
    }
    r = requests.get(url, params=params)
    if r.status_code != 200:
        return None
    data = r.json()
    if data.get("status") != "OK":
        return None
    element = data["rows"][0]["elements"][0]
    if element.get("status") != "OK":
        return None
    meters = element["distance"]["value"]
    return meters/1609.34 if unit=='mi' else meters/1000.0

def filter_by_distance_using_google_maps(pets, user_lat, user_lng, max_dist, unit='km'):
    """
    pets: list of Pet objs with .latitude/.longitude
    user_lat/lng: floats
    max_dist: numeric radius
    unit: 'km' or 'mi'
    Returns list of pets within max_dist, each with .distance set.
    """
    origin = (user_lat, user_lng)
    out = []
    for pet in pets:
        if pet.latitude is None or pet.longitude is None:
            continue
        dest = (pet.latitude, pet.longitude)
        dist = get_distance_via_google(origin, dest, unit=unit)
        if dist is None:
            continue
        pet.distance = dist
        if dist <= max_dist:
            out.append(pet)
    return out
