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

# Kontrola aktuálneho času v Prahe
praha_tz = pytz.timezone('Europe/Prague')
now = datetime.now(praha_tz)
print(f"Aktuálny čas v Prahe: {now}")

if now.hour == 7 and now.minute == 0:
    # Poslanie GET requestu na API
    url = "https://api.golemio.cz/v2/libraries"
    headers = {"X-Access-Token": API_KEY}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        libraries = data['features']
        
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
        df.to_csv('libraries.csv', index=False)
        print("Dáta boli úspešne extrahované a uložené do 'libraries.csv'.")
    else:
        print(f"Chyba pri získavaní dát: {response.status_code}")
else:
    print("Nie je 7:00, extrakcia sa nespustí.")