from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Pet(db.Model):
    __tablename__ = "pets"

    id             = db.Column(db.Integer,   primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    pet_type       = db.Column(db.String(10),  nullable=False)  # dog / cat
    age            = db.Column(db.Integer,    nullable=False)
    breed          = db.Column(db.String(100), nullable=False)
    behavior       = db.Column(db.String(100), nullable=False)
    color          = db.Column(db.String(50),  nullable=False)
    hypoallergenic = db.Column(db.String(3),   nullable=False)  # Yes / No
    size           = db.Column(db.String(10),  nullable=False)  # Small / Medium / Large
    care_level     = db.Column(db.String(10),  nullable=False)  # Low / Medium / High
    address        = db.Column(db.String(200), nullable=False)  # Shelter’s raw input address
    latitude       = db.Column(db.Float,       nullable=False)
    longitude      = db.Column(db.Float,       nullable=False)

    # Transient property to hold computed distance (not in DB)
    @property
    def distance(self):
        return getattr(self, "_distance", None)

    @distance.setter
    def distance(self, value):
        setattr(self, "_distance", value)
