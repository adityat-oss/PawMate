
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

download the repository and navigate to the PawMate FOLDER path in your command line
you need to run these commands if you haven't already done so
- pip install flask
- pip install requests
- pip install pip install flask_sqlalchemy

- After these installations all you need is a Google Maps API Key to use the location functionality
- navigate to google cloud console and enable an api. You need enable the Geocoding, Distance Matrix and Maps JavaScript APIs. Once you have your API Key you can run the command
- export GOOGLE_MAPS_API_KEY="YOUR-KEY" #replace YOUR-KEY with your api key
- after this run the main.py in terminal and the webapp will be launched locally

**THIS IS A DEMO**
