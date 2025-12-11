import math
import requests
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Storage for map data
shelters = []
volunteers = []
aid = []

@app.route('/add_shelter', methods=['POST'])
def add_shelter_api():
    data = request.get_json()
    name = data.get('name')
    lat = data.get('lat')
    lon = data.get('lon')
    cap = data.get('cap')
    shelters.append({"name": name, "lat": lat, "lon": lon, "cap": cap})
    print("New shelter added:", name, lat, lon, cap)
    return jsonify({"message": "Shelter added successfully"}), 200

@app.route('/', methods=['GET'])
def home():
    return "SafeHaven Flask server is running!", 200

@app.route('/closest_shelter', methods=['POST'])
def closest_shelter():
    data = request.get_json()
    user_lat = float(data['lat'])
    user_lon = float(data['lon'])

    nearest = None
    min_distance = float('inf')
    R = 6371.0  # Earth radius in km

    for s in shelters:
        lat2 = s['lat']
        lon2 = s['lon']

        lat1_rad = math.radians(user_lat)
        lon1_rad = math.radians(user_lon)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = R * c

        if d < min_distance:
            min_distance = d
            nearest = s

    if nearest:
        return jsonify({
            "name": nearest['name'],
            "lat": nearest['lat'],
            "lon": nearest['lon'],
            "cap": nearest['cap'],
            "distance": round(min_distance, 2)
        }), 200
    else:
        return jsonify({"error": "No shelters available"}), 404

@app.route('/request_aid', methods=['POST'])
def request_aid():
    data = request.get_json()
    name = data.get('name')
    aid_type = data.get('type_of_aid')  
    lat = data.get('latitude')
    lon = data.get('longitude')

    if not name or not aid_type or lat is None or lon is None:
        print("Missing data fields!")
        return jsonify({"error": "Missing data"}), 400

    location = f"{lat},{lon}"

    aid.append({
        "name": name,
        "aid_type": aid_type,
        "location": location
    })

    print("Aid request received from", name, ":", aid_type, "at", location)
    return jsonify({"message": "Aid request received successfully!"}), 200

@app.route('/register_volunteer', methods=['POST'])
def register_volunteer():
    data = request.get_json()
    name = data.get('name')
    skill = data.get('skill')
    phone = data.get('phone')
    lat = data.get('latitude')
    lon = data.get('longitude')

    if not name or not skill or not phone or lat is None or lon is None:
        return jsonify({"error": "Missing data"}), 400

    volunteers.append({
        "name": name,
        "skill": skill,
        "phone": phone,
        "location": f"{lat},{lon}"
    })

    print("New volunteer registered:", name, skill, phone, lat, lon)
    return jsonify({"message": "Volunteer registered successfully!"}), 200

@app.route('/get_shelters', methods=['GET'])
def get_shelters():
    return jsonify(shelters), 200

@app.route('/get_aid_requests', methods=['GET'])
def get_aid_requests():
    return jsonify(aid), 200

@app.route('/entries', methods=['GET'])
def get_all_entries():
    combined = []

    for s in shelters:
        combined.append({
            "type": "shelter",
            "name": s["name"],
            "lat": s["lat"],
            "lon": s["lon"],
            "capacity": s["cap"]
        })

    for a in aid:
        lat, lon = map(float, a["location"].split(","))
        combined.append({
            "type": "aid",
            "name": a["name"],
            "lat": lat,
            "lon": lon,
            "requestType": a["aid_type"]
        })

    return jsonify(combined), 200

# Run the app using Railway's port or default 5000
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
