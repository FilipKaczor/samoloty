
import requests
import time
import math
from datetime import datetime

# Lokalizacja obserwacji
lat = 50.09771497596586
lon = 19.87453304052037

# Promień w milach morskich (API ADSB.lol używa NM)
radius = 2

# Co ile sekund odświeżać dane
refresh_interval = 15

url = (
    f"https://api.adsb.lol/v2/"
    f"lat/{lat}/lon/{lon}/dist/{radius}"
)

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = (
        math.sin(dp / 2)**2
        + math.cos(p1) * math.cos(p2)
        * math.sin(dl / 2)**2
    )

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))


def get_direction(degrees):
    if degrees is None:
        return "Brak danych"

    directions = [
        "N", "NE", "E", "SE",
        "S", "SW", "W", "NW"
    ]

    return directions[int((degrees % 360) / 45 + 0.5) % 8]


print("===================================")
print("       HOME AIR RADAR")
print("===================================")
print(f"Lokalizacja: {lat}, {lon}")
print(f"Promień API: {radius} NM")
print(f"Odświeżanie: {refresh_interval} sekund")
print("Naciśnij CTRL+C, aby zakończyć.")
print("===================================")

while True:
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        data = response.json()
        aircraft = data.get("ac", [])

        print("\n" + "=" * 65)
        print("AKTUALIZACJA:", datetime.now().strftime("%H:%M:%S"))
        print("Liczba wykrytych samolotów:", len(aircraft))
        print("=" * 65)

        if not aircraft:
            print("Brak wykrytych samolotów w tym momencie.")

        for plane in aircraft:
            plane_lat = plane.get("lat")
            plane_lon = plane.get("lon")

            distance = None

            if plane_lat is not None and plane_lon is not None:
                distance = calculate_distance(
                    lat, lon, plane_lat, plane_lon
                )

            heading = plane.get("track")

            altitude = plane.get("alt_baro")
            if altitude == "ground":
                altitude = "Na ziemi"

            print("\n✈ SAMOLOT")
            print("-" * 40)
            print("Callsign:", plane.get("flight", "Brak"))
            print("ICAO:", plane.get("hex", "Brak"))
            print("Typ:", plane.get("t", "Brak"))
            print("Rejestracja:", plane.get("r", "Brak"))
            print("Wysokość:", altitude, "ft")
            print("Prędkość:", plane.get("gs"), "węzłów")
            print("Kierunek:", get_direction(heading))
            print("Kąt:", heading, "stopni")
            print("Pozycja:", plane_lat, plane_lon)

            if distance is not None:
                print(f"Odległość od domu: {distance:.2f} km")

        print("\nNastępne pobieranie za", refresh_interval, "sekund...")

    except requests.exceptions.Timeout:
        print("Błąd: przekroczono czas oczekiwania na API.")

    except requests.exceptions.RequestException as e:
        print("Błąd połączenia:", e)

    except Exception as e:
        print("Nieoczekiwany błąd:", e)

    time.sleep(refresh_interval)
