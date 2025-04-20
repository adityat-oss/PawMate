import os, requests

key = os.getenv("GOOGLE_MAPS_API_KEY")
print("AIzaSyC4AIjtCAWcnTcNiH0ujX1udPyB7f5deew", key)

address = "1600 Amphitheatre Parkway, Mountain View, CA"
resp = requests.get(
    "https://maps.googleapis.com/maps/api/geocode/json",
    params={"address": address, "key": key}
)
data = resp.json()
print("HTTP status:", resp.status_code)
print("API status:", data.get("status"))
if "error_message" in data:
    print("Error message:", data["error_message"])
else:
    print("First result geometry:", data["results"][0]["geometry"])
