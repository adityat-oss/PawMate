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
        
        # Debug which fields are empty
        empty_fields = [k for k, v in fields.items() if not v]
        if empty_fields:
            flash(f"Missing fields: {', '.join(empty_fields)}", "error")
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
    pet_type    = request.values.get("pet_type", "").strip()
    breed       = request.values.get("breed", "").strip()
    behavior    = request.values.get("behavior", "").strip()
    care_level  = request.values.get("care_level", "").strip()
    size        = request.values.get("size", "").strip()
    age_min_str = request.values.get("age_min", "").strip()
    age_max_str = request.values.get("age_max", "").strip()
    dist_str    = request.values.get("distance", "").strip()
    unit        = request.values.get("distance_unit", "mi")
    loc_mode    = request.values.get("loc_mode", "ip")
    manual_addr = request.values.get("manual_address", "").strip()
    name        = request.values.get("name", "").strip()

    # Convert numeric filters
    age_min = int(age_min_str) if age_min_str.isdigit() else None
    age_max = int(age_max_str) if age_max_str.isdigit() else None
    distance = float(dist_str) if dist_str.replace(".", "", 1).isdigit() else None

    # Build SQL query filters
    q = Pet.query
    if pet_type:   q = q.filter_by(pet_type=pet_type)
    if breed:      q = q.filter_by(breed=breed)
    if behavior:   q = q.filter_by(behavior=behavior)
    if care_level: q = q.filter_by(care_level=care_level)
    if size:       q = q.filter_by(size=size)
    if name:       q = q.filter(Pet.name.ilike(f"%{name}%"))
    if age_min is not None: q = q.filter(Pet.age >= age_min)
    if age_max is not None: q = q.filter(Pet.age <= age_max)
    candidates = q.all()

    pets = candidates

    # Determine user's coords for distance filtering
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
        pet_type=pet_type,
        breed=breed,
        behavior=behavior,
        care_level=care_level,
        size=size,
        age_min=age_min_str,
        age_max=age_max_str,
        distance=dist_str,
        distance_unit=unit,
        loc_mode=loc_mode,
        manual_address=manual_addr,
        name=name,
    )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
