# 🌟 Natal Chart API

A RESTful API service that calculates astrological natal charts using the Swiss Ephemeris library. The API provides planetary positions, house cusps, ascendant, and aspects for a given birth date, time, and location.

## 🔐 Authentication

All API endpoints are protected and require authentication using an API key. You must include your API key in the `X-API-Key` header with every request.

```bash
X-API-Key: your_api_key_here
```

## 🛠️ Endpoints

### 🏥 Health Check
- **URL**: `/`
- **Method**: `GET`
- **Authentication**: Required
- **Response**: Text indicating the API is running

### 📊 Generate Natal Chart
- **URL**: `/chart`
- **Method**: `POST`
- **Authentication**: Required
- **Content-Type**: `application/json`

#### Request Body

```json
{
    "birth_date": "YYYY-MM-DD",
    "birth_time": "HH:MM",
    "birth_place": {
        "latitude": float,
        "longitude": float,
        "timezone": float
    }
}
```

| Field | Type | Description |
|-------|------|-------------|
| birth_date | string | Date of birth in YYYY-MM-DD format |
| birth_time | string | Time of birth in 24-hour HH:MM format |
| birth_place.latitude | float | Latitude of birth location (-90 to 90) |
| birth_place.longitude | float | Longitude of birth location (-180 to 180) |
| birth_place.timezone | float | Timezone offset from UTC in hours |

#### 📝 Response

```json
{
    "planets": {
        "Sun": float,
        "Moon": float,
        "Mercury": float,
        "Venus": float,
        "Mars": float,
        "Jupiter": float,
        "Saturn": float,
        "Uranus": float,
        "Neptune": float,
        "Pluto": float
    },
    "ascendant": float,
    "houses": [float, float, ...],  // 12 house cusps
    "aspects": [
        {
            "between": [string, string],
            "aspect": string,
            "orb": float
        }
    ]
}
```

All angles are returned in degrees (0-360).

#### 💻 Example Request

```bash
curl -X POST https://natal-chart-api-22rt.onrender.com/chart \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "birth_date": "1995-06-14",
    "birth_time": "14:25",
    "birth_place": {
      "latitude": 34.0522,
      "longitude": -118.2437,
      "timezone": -7
    }
  }'
```

## ⚠️ Error Responses

| Status Code | Description |
|------------|-------------|
| 401 | Invalid or missing API key |
| 400 | Invalid request body or parameters |
| 500 | Server error |

## 🔧 Technical Details

- 🐍 Built with Python and Flask
- 🌌 Uses Swiss Ephemeris library for astronomical calculations
- 🏠 Supports Placidus house system
- 📐 Calculates aspects with 6° orb
- ⭐ Includes major aspects:
  - Conjunction (0°) ☌
  - Sextile (60°) ⚹
  - Square (90°) □
  - Trine (120°) △
  - Opposition (180°) ☍

## 🚀 Deployment

The API is deployed on Render as a web service. Make sure to set the `API_KEY` environment variable in your Render dashboard for authentication to work properly.