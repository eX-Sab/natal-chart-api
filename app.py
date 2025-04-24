from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import math
import os
from functools import wraps

app = Flask(__name__)

# Set ephemeris path relative to the application directory
ephe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ephe')
swe.set_ephe_path(ephe_path)

# Verify ephemeris files are accessible
try:
    # Test calculation to verify ephemeris files
    test_jd = swe.julday(2000, 1, 1, 0)
    swe.calc_ut(test_jd, swe.SUN)
except Exception as e:
    print(f"Error initializing Swiss Ephemeris: {e}")
    print(f"Looking for files in: {ephe_path}")
    print(f"Directory contents: {os.listdir(ephe_path) if os.path.exists(ephe_path) else 'Directory not found'}")

# Get API key from environment variable
API_KEY = os.environ.get('API_KEY')
if not API_KEY:
    raise ValueError("API_KEY environment variable must be set")

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != API_KEY:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated_function

PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
    "North Node": swe.MEAN_NODE,
    "Chiron": swe.CHIRON
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", 
    "Leo", "Virgo", "Libra", "Scorpio", 
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

ELEMENTS = {
    "Fire": ["Aries", "Leo", "Sagittarius"],
    "Earth": ["Taurus", "Virgo", "Capricorn"],
    "Air": ["Gemini", "Libra", "Aquarius"],
    "Water": ["Cancer", "Scorpio", "Pisces"]
}

MODALITIES = {
    "Cardinal": ["Aries", "Cancer", "Libra", "Capricorn"],
    "Fixed": ["Taurus", "Leo", "Scorpio", "Aquarius"],
    "Mutable": ["Gemini", "Virgo", "Sagittarius", "Pisces"]
}

ASPECTS = {
    "Conjunction": 0,
    "Sextile": 60,
    "Square": 90,
    "Trine": 120,
    "Opposition": 180
}

def get_sign(degree):
    sign_num = int(degree / 30)
    degree_in_sign = degree % 30
    return SIGNS[sign_num], round(degree_in_sign, 2)

def get_house(degree, houses):
    for i in range(len(houses)):
        next_house = houses[(i + 1) % 12]
        if next_house < houses[i]:  # Handle house crossing 0°
            if degree >= houses[i] or degree < next_house:
                return i + 1
        elif houses[i] <= degree < next_house:
            return i + 1
    return 1

def get_element_modal_dist(positions):
    elemental = {"Fire": 0, "Earth": 0, "Water": 0, "Air": 0}
    modal = {"Cardinal": 0, "Fixed": 0, "Mutable": 0}
    
    for planet_data in positions.values():
        sign = planet_data["sign"]
        for element, signs in ELEMENTS.items():
            if sign in signs:
                elemental[element] += 1
        for modality, signs in MODALITIES.items():
            if sign in signs:
                modal[modality] += 1
    
    return elemental, modal

def normalize_angle(angle):
    return angle % 360

def get_aspects(positions):
    results = []
    planets = list(positions.keys())
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            p1, p2 = planets[i], planets[j]
            # Skip aspects with North Node and Chiron
            if p1 in ["North Node", "Chiron"] or p2 in ["North Node", "Chiron"]:
                continue
            lon1 = positions[p1]["degree"] + (SIGNS.index(positions[p1]["sign"]) * 30)
            lon2 = positions[p2]["degree"] + (SIGNS.index(positions[p2]["sign"]) * 30)
            angle = abs(lon1 - lon2)
            angle = min(angle, 360 - angle)
            
            for aspect_name, aspect_angle in ASPECTS.items():
                orb = abs(angle - aspect_angle)
                if orb <= 6:  # 6° orb
                    results.append({
                        "type": aspect_name,
                        "between": [p1, p2],
                        "orb": round(orb, 2)
                    })
    return results

@app.route("/", methods=["GET"])
@require_api_key
def home():
    return "Swiss Ephemeris API is running!"

@app.route("/chart", methods=["POST"])
@require_api_key
def generate_chart():
    data = request.json
    birth_date = data["birth_date"]  # format: YYYY-MM-DD
    birth_time = data["birth_time"]  # format: HH:MM
    place = data["birth_place"]

    year, month, day = map(int, birth_date.split("-"))
    hour, minute = map(int, birth_time.split(":"))

    # Convert to UT
    timezone = place["timezone"]
    ut_hour = hour - timezone + minute / 60.0

    jd_ut = swe.julday(year, month, day, ut_hour)

    # Calculate houses first
    lat = place["latitude"]
    lon = place["longitude"]
    houses, ascmc = swe.houses_ex(jd_ut, lat, lon, b'P')  # Placidus
    ascendant = ascmc[0]
    house_cusps = [normalize_angle(h) for h in houses]

    # Calculate planet positions with the new format
    positions = {}
    
    # Add Ascendant first
    asc_sign, asc_degree = get_sign(ascendant)
    positions["Ascendant"] = {
        "sign": asc_sign,
        "degree": asc_degree
    }

    # Calculate planet positions
    for name, pid in PLANETS.items():
        result, _ = swe.calc_ut(jd_ut, pid)
        lon = normalize_angle(result[0])
        sign, degree = get_sign(lon)
        house = get_house(lon, house_cusps)
        
        positions[name] = {
            "sign": sign,
            "degree": degree,
            "house": house
        }

    # Calculate aspects
    aspects = get_aspects(positions)

    # Calculate distributions
    elemental_dist, modal_dist = get_element_modal_dist(positions)

    return jsonify({
        **positions,
        "aspects": aspects,
        "elemental_distribution": elemental_dist,
        "modal_distribution": modal_dist
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))