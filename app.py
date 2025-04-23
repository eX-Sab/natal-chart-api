from flask import Flask, request, jsonify
import swisseph as swe
import datetime
import math

import os

app = Flask(__name__)
swe.set_ephe_path("./ephe")

@app.route("/chart", methods=["POST"])
def generate_chart():
    data = request.json
    # ... process natal chart
    return jsonify({"status": "success", "message": "Chart data here"})

@app.route("/", methods=["GET"])
def home():
    return "Swiss Ephemeris API is running!"
    
def calculate_aspects(planet_positions):
    aspects = []
    aspect_angles = {
        "Conjunction": 0,
        "Opposition": 180,
        "Trine": 120,
        "Square": 90,
        "Sextile": 60
    }
    orb = 6  # degrees of allowable difference

    planets = list(planet_positions.items())
    for i in range(len(planets)):
        for j in range(i + 1, len(planets)):
            name1, pos1 = planets[i]
            name2, pos2 = planets[j]
            angle = abs(pos1 - pos2)
            if angle > 180:
                angle = 360 - angle
            for aspect_name, aspect_angle in aspect_angles.items():
                if abs(angle - aspect_angle) <= orb:
                    aspects.append({
                        "planet1": name1,
                        "planet2": name2,
                        "aspect": aspect_name,
                        "angle": round(angle, 2)
                    })
    return aspects

@app.route('/natal-chart', methods=['POST'])
def natal_chart():
    data = request.json
    birth_date = data['birth_date']  # e.g., '1990-05-15'
    birth_time = data['birth_time']  # e.g., '14:30'
    lat = float(data['latitude'])
    lon = float(data['longitude'])

    dt = datetime.datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    jd_ut = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60.0)

    planet_positions = {}
    for planet in range(swe.SUN, swe.PLUTO + 1):
        pos, _ = swe.calc_ut(jd_ut, planet)
        planet_positions[swe.get_planet_name(planet)] = pos[0]

    # Ascendant and Houses
    hsys = 'P'  # Placidus
    cusps, ascmc = swe.houses(jd_ut, lat, lon, hsys)

    return jsonify({
        "julian_day": jd_ut,
        "planet_positions": planet_positions,
        "aspects": calculate_aspects(planet_positions),
        "ascendant": ascmc[0],
        "houses": cusps[:12]
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
