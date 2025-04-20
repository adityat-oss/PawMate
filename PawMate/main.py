import os
import requests
from flask import Flask, render_template, request, flash
from models import db, Pet
from utils import (
    geocode_address,
    get_user_location_by_ip,
    filter_by_distance_using_google_maps,
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]        = "sqlite:///pets.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key                              = os.getenv("FLASK_SECRET", "change‑me")

db.init_app(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/adoption_center", methods=["GET", "POST"])
def adoption_center():
    if request.method == "POST":
        fields = {k: request.form.get(k, "").strip() for k in
                  ["name","age","breed","pet_type","behavior",
                   "color","hypoallergenic","size","care_level",
                   "address"]}
        if not all(fields.values()):
            flash("All fields required.", "error")
            return render_template("adoption_center.html")

        try:
            age = int(fields["age"])
        except ValueError:
            flash("Age must be numeric.", "error")
            return render_template("adoption_center.html")

        coords = geocode_address(fields["address"])
        if not coords:
            flash("Invalid address.", "error")
            return render_template("adoption_center.html")

        pet = Pet(
            name           = fields["name"],
            pet_type       = fields["pet_type"],
            age            = age,
            breed          = fields["breed"],
            behavior       = fields["behavior"],
            color          = fields["color"],
            hypoallergenic = fields["hypoallergenic"],
            size           = fields["size"],
            care_level     = fields["care_level"],
            address        = fields["address"],    # store raw input
            latitude       = coords[0],
            longitude      = coords[1]
        )
        db.session.add(pet)
        db.session.commit()
        flash("Pet posted!", "success")
    return render_template("adoption_center.html")

@app.route("/petsitter", methods=["GET", "POST"])
def petsitter():
    # Collect filters
    breed       = request.values.get("breed", "").strip()
    behavior    = request.values.get("behavior", "").strip()
    care_level  = request.values.get("care_level", "").strip()
    age_str     = request.values.get("age", "").strip()
    dist_str    = request.values.get("distance", "").strip()
    unit        = request.values.get("distance_unit", "mi")
    loc_mode    = request.values.get("loc_mode", "ip")      # 'ip' or 'manual'
    manual_addr = request.values.get("manual_address", "").strip()

    age = int(age_str) if age_str.isdigit() else None
    distance = float(dist_str) if dist_str.replace(".", "", 1).isdigit() else None

    # Build SQL query filters
    q = Pet.query
    if breed:      q = q.filter_by(breed=breed)
    if behavior:   q = q.filter_by(behavior=behavior)
    if care_level: q = q.filter_by(care_level=care_level)
    if age is not None: q = q.filter_by(age=age)
    candidates = q.all()

    pets = candidates

    # Determine user’s coords for distance filtering
    user_lat = user_lng = None
    if loc_mode == "ip":
        ip = request.remote_addr
        if ip in ("127.0.0.1", "::1"):
            try:
                ip = requests.get("https://api.ipify.org").text
            except:
                flash("Cannot fetch public IP.", "error")
                ip = None
        if ip:
            loc = get_user_location_by_ip(ip)
            if loc:
                user_lat, user_lng = loc
            else:
                flash("Could not geolocate IP.", "error")
    else:  # manual
        if manual_addr:
            loc = geocode_address(manual_addr)
            if loc:
                user_lat, user_lng = loc
            else:
                flash("Could not geocode address.", "error")

    # Apply distance filter if valid
    if user_lat is not None and distance is not None:
        pets = filter_by_distance_using_google_maps(
            candidates, user_lat, user_lng, distance, unit
        )

    return render_template(
        "petsitter.html",
        pets=pets,
        breed=breed,
        behavior=behavior,
        care_level=care_level,
        age=age_str,
        distance=dist_str,
        distance_unit=unit,
        loc_mode=loc_mode,
        manual_address=manual_addr,
    )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
