import sys
import requests

BASE_GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
BASE_WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

def get_coordinates(city_name: str) -> tuple[float, float]:
    """Получает координаты города по его названию."""
    params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
    try:
        response = requests.get(BASE_GEO_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "results" not in data or not data["results"]:
            raise ValueError(f"Город '{city_name}' не найден")
        result = data["results"][0]
        return result["latitude"], result["longitude"]
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ошибка сети при поиске города: {e}")
    except KeyError as e:
        raise RuntimeError(f"Некорректный ответ от геокодера: {e}")

def get_weather(lat: float, lon: float) -> dict:
    """Получает текущую погоду по координатам."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "timezone": "auto"
    }
    try:
        response = requests.get(BASE_WEATHER_URL, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Ошибка сети при запросе погоды: {e}")

def main():
    if len(sys.argv) != 2:
        print("Использование: python weather_cli.py <город>")
        sys.exit(1)

    city = sys.argv[1]

    try:
        print(f"Поиск города: {city}...")
        lat, lon = get_coordinates(city)
        print(f"Координаты: {lat:.2f}, {lon:.2f}")

        print("Запрос погоды...")
        weather_data = get_weather(lat, lon)

        current = weather_data["current_weather"]
        timezone = weather_data["timezone"]
        print("\n🌤️ Текущая погода:")
        print(f"Город: {city}")
        print(f"Температура: {current['temperature']}°C")
        print(f"Скорость ветра: {current['windspeed']} км/ч")
        print(f"Направление ветра: {current['winddirection']}°")
        print(f"Время: {current['time']} ({timezone})")

    except (ValueError, RuntimeError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()