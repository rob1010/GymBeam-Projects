import os
import json
import requests
import pandas as pd
from datetime import datetime
import pytz

# Získanie API kľúča z environment variable
API_KEY = os.getenv('GOLEMIO_API_KEY')
if not API_KEY:
    raise ValueError("API kľúč nie je nastavený. Nastavte ho ako environment variable 'GOLEMIO_API_KEY'.")

# Ensure API key is a string and strip any whitespace
API_KEY = str(API_KEY).strip()

# Debug: Check for problematic characters
print(f"API key type: {type(API_KEY)}")
print(f"API key length: {len(API_KEY)}")
print(f"API key repr: {repr(API_KEY[:10])}..." if len(API_KEY) > 10 else f"API key repr: {repr(API_KEY)}")

# Check for non-ASCII characters
try:
    API_KEY.encode('ascii')
    print("API key contains only ASCII characters")
except UnicodeEncodeError:
    print("WARNING: API key contains non-ASCII characters")
    API_KEY = API_KEY.encode('ascii', 'ignore').decode('ascii')
    print(f"Cleaned API key length: {len(API_KEY)}")

# Kontrola aktuálneho času v Prahe
praha_tz = pytz.timezone('Europe/Prague')
now = datetime.now(praha_tz)
print(f"Aktuálny čas v Prahe: {now}")

# Poslanie GET requestu na API
url = "https://api.golemio.cz/v2/libraries"
headers = {
    "X-Access-Token": API_KEY,
    "Content-Type": "application/json",
    "User-Agent": "GitHub-Actions-Bot/1.0"
}

print(f"Making request to: {url}")
print(f"Headers: {dict((k, 'HIDDEN' if 'token' in k.lower() else v) for k, v in headers.items())}")

try:
    response = requests.get(url, headers=headers, timeout=30)
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        libraries = data['features']
        print(f"Found {len(libraries)} libraries")
        
        # Extrakcia požadovaných parametrov
        extracted_data = []
        for library in libraries:
            props = library.get('properties', {})
            address = props.get('address', {})
            geo = library.get('geometry', {}).get('coordinates', [None, None])
            opening_hours = json.dumps(props.get('openingHours', []))
            
            extracted_data.append({
                'ID knižnice': props.get('id', 'N/A'),
                'Názov knižnice': props.get('name', 'N/A'),
                'Ulica': address.get('street', 'N/A'),
                'PSČ': address.get('postalCode', 'N/A'),
                'Mesto': address.get('city', 'N/A'),
                'Kraj': address.get('region', 'N/A'),
                'Krajina': address.get('country', 'N/A'),
                'Zemepisná šírka': geo[1] if geo[1] else 'N/A',
                'Zemepisná dĺžka': geo[0] if geo[0] else 'N/A',
                'Čas otvorenia': opening_hours
            })
        
        # Uloženie do DataFrame a CSV
        df = pd.DataFrame(extracted_data)
        df.to_csv('libraries.csv', index=False, encoding='utf-8')
        print("Dáta boli úspešne extrahované a uložené do 'libraries.csv'.")
        print(f"Saved {len(extracted_data)} records to CSV")
        
    elif response.status_code == 401:
        print("Chyba 401: Neplatný API kľúč alebo chýbajúce oprávnenia")
        print("Skontrolujte, či je API kľúč správne nastavený v GitHub Secrets")
    elif response.status_code == 403:
        print("Chyba 403: Prístup zamietnutý - skontrolujte oprávnenia API kľúča")
    elif response.status_code == 429:
        print("Chyba 429: Príliš veľa požiadaviek - API limit dosiahnutý")
    else:
        print(f"Chyba pri získavaní dát: {response.status_code}")
        print(f"Response text: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    print("Chyba: Časový limit požiadavky vypršal")
except requests.exceptions.ConnectionError:
    print("Chyba: Problém s pripojením k API")
except requests.exceptions.RequestException as e:
    print(f"Chyba pri HTTP požiadavke: {e}")
except json.JSONDecodeError:
    print("Chyba: Neplatná JSON odpoveď z API")
except Exception as e:
    print(f"Neočakávaná chyba: {e}")
    raise