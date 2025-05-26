import os
import json
import requests
import pandas as pd
from datetime import datetime
import pytz
from tenacity import retry, stop_after_attempt, wait_exponential

API_KEY = os.getenv('GOLEMIO_API_KEY')
if not API_KEY:
    print("Error: API key not set")
    df = pd.DataFrame(columns=['ID knižnice', 'Názov knižnice', 'Ulica', 'PSČ', 'Mesto', 'Kraj', 'Krajina', 'Zemepisná šírka', 'Zemepisná dĺžka', 'Čas otvorenia'])
    df.to_csv('libraries.csv', index=False, encoding='utf-8')
    print("Created empty libraries.csv with headers due to missing API key")
    exit(0)

API_KEY = str(API_KEY).strip()
print(f"API key length: {len(API_KEY)}")
try:
    API_KEY.encode('ascii')
    print("API key contains only ASCII characters")
except UnicodeEncodeError:
    print("WARNING: API key contains non-ASCII characters")
    API_KEY = API_KEY.encode('ascii', 'ignore').decode('ascii')

praha_tz = pytz.timezone('Europe/Prague')
now = datetime.now(praha_tz)
print(f"Aktuálny čas v Prahe: {now}")

url = "https://api.golemio.cz/v2/municipal-libraries"  # Update to correct endpoint
headers = {
    "X-Access-Token": API_KEY,
    "Content-Type": "application/json",
    "User-Agent": "GitHub-Actions-Bot/1.0"
}

print(f"Making request to: {url}")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def make_api_request():
    return requests.get(url, headers=headers, timeout=30)

try:
    response = make_api_request()
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Raw response: {json.dumps(data, indent=2)[:1000]}...")
        libraries = data.get('features', [])
        if not libraries:
            print("Warning: No libraries found in API response")
            df = pd.DataFrame(columns=['ID knižnice', 'Názov knižnice', 'Ulica', 'PSČ', 'Mesto', 'Kraj', 'Krajina', 'Zemepisná šírka', 'Zemepisná dĺžka', 'Čas otvorenia'])
            df.to_csv('libraries.csv', index=False, encoding='utf-8')
            print("Created empty libraries.csv with headers")
            exit(0)
        
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
        
        df = pd.DataFrame(extracted_data)
        df.to_csv('libraries.csv', index=False, encoding='utf-8')
        print(f"Saved {len(extracted_data)} records to libraries.csv")
    
    else:
        print(f"Error: Status code {response.status_code}")
        print(f"Full response text: {response.text}")
        df = pd.DataFrame(columns=['ID knižnice', 'Názov knižnice', 'Ulica', 'PSČ', 'Mesto', 'Kraj', 'Krajina', 'Zemepisná šírka', 'Zemepisná dĺžka', 'Čas otvorenia'])
        df.to_csv('libraries.csv', index=False, encoding='utf-8')
        print("Created empty libraries.csv with headers due to API error")
        exit(0)

except requests.exceptions.RequestException as e:
    print(f"HTTP request error: {e}")
    df = pd.DataFrame(columns=['ID knižnice', 'Názov knižnice', 'Ulica', 'PSČ', 'Mesto', 'Kraj', 'Krajina', 'Zemepisná šírka', 'Zemepisná dĺžka', 'Čas otvorenia'])
    df.to_csv('libraries.csv', index=False, encoding='utf-8')
    print("Created empty libraries.csv with headers due to HTTP error")
    exit(0)
except json.JSONDecodeError:
    print("Error: Invalid JSON response from API")
    df = pd.DataFrame(columns=['ID knižnice', 'Názov knižnice', 'Ulica', 'PSČ', 'Mesto', 'Kraj', 'Krajina', 'Zemepisná šírka', 'Zemepisná dĺžka', 'Čas otvorenia'])
    df.to_csv('libraries.csv', index=False, encoding='utf-8')
    print("Created empty libraries.csv with headers due to JSON error")
    exit(0)
except Exception as e:
    print(f"Unexpected error: {e}")
    df = pd.DataFrame(columns=['ID knižnice', 'Názov knižnice', 'Ulica', 'PSČ', 'Mesto', 'Kraj', 'Krajina', 'Zemepisná šírka', 'Zemepisná dĺžka', 'Čas otvorenia'])
    df.to_csv('libraries.csv', index=False, encoding='utf-8')
    print("Created empty libraries.csv with headers due to unexpected error")
    exit(0)