import requests
import json

HEADERS = {'User-Agent': 'Mimid/1.0'}

def test_query(q):
    print(f"Testing query: [{q}]")
    url = "https://xeno-canto.org/api/2/recordings"
    try:
        resp = requests.get(url, params={'query': q}, headers=HEADERS)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            num = data.get('numRecordings')
            print(f"Found: {num}")
            if num and int(num) > 0:
                print("First record:", data['recordings'][0]['en'], data['recordings'][0]['length'])
        else:
            print("Response:", resp.text[:200])
    except Exception as e:
        print(f"Error: {e}")

# Test 1: Simple
test_query('Hairy Woodpecker')

# Test 2: With quotes
test_query('en:"Hairy Woodpecker"')

# Test 3: With Country
test_query('en:"Hairy Woodpecker" cnt:"United States"')

# Test 4: Full query used in app
test_query('en:"Hairy Woodpecker" cnt:"United States" q:A len:10-60')
