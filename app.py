from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import math
import os

app = Flask(__name__)
swe.set_ephe_path("./ephe")

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
    "Pluto": swe.PLUTO
}

ASPECTS = {
    "Conjunction": 0,
    "Sextile": 60,
    "Square": 90,
    "Trine": 120,
    "Opposition": 180
}

def normalize_angle(angle):
    return angle % 360

def get_aspects(planets):
    results = []
    items = list(planets.items())
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            p1, lon1 = items[i]
            p2, lon2 = items[j]
            angle = abs(lon1 - lon2)
            angle = min(angle, 360 - angle)
            for name, target in ASPECTS.items():
                if abs(angle - target) <= 6:  # 6° orb
                    results.append({
                        "between": [p1, p2],
                        "aspect": name,
                        "orb": round(abs(angle - target), 2)
                    })
    return results

@app.route("/", methods=["GET"])
def home():
    return "Swiss Ephemeris API is running!"

@app.route("/chart", methods=["POST"])
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

    # Planet positions
    planet_positions = {}
    for name, pid in PLANETS.items():
        lon, _, _ = swe.calc_ut(jd_ut, pid)[0:3]
        planet_positions[name] = round(lon, 6)

    # Ascendant & houses
    lat = place["latitude"]
    lon = place["longitude"]
    ascmc, houses, _ = swe.houses_ex(jd_ut, lat, lon, b'P')  # Placidus
    ascendant = round(ascmc[0], 6)
    house_cusps = [round(h, 6) for h in houses]

    # Aspects
    aspects = get_aspects(planet_positions)

    return jsonify({
        "planets": planet_positions,
        "ascendant": ascendant,
        "houses": house_cusps,
        "aspects": aspects
    })