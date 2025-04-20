# PawMate
Pet Adoption & Petsitter Matching App
A simple flask based web application that lets pet shelters connect with a community of pet shelters
** Adoption Center**
- Post a pet with its name, type, age, breed, behavior, color, hypoallergenic status, size and care level
- Address is geocoded for your shelter
** Petsitter **
- Filter based on parameters
- toggle location source
- specify distance you are looking for
- distance is computed via Google APIs. You need a google api key to be able to use location features**
- displays all pets by default

- ## Tech Stack

- Python 3.8+  
- Flask  
- SQLite (via SQLAlchemy)  
- Requests  
- Google Maps APIs: Geocoding & Distance Matrix  

---

##  Quick Start

### 1. Clone & Virtualenv

```bash
git clone https://github.com/your‑username/pet‑match‑app.git
cd pet‑match‑app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
