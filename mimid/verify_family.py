import requests
import json

def test_search():
    try:
        # Search for Ostrich
        resp = requests.get('http://localhost:5000/api/search?query=en:"Common Ostrich"')
        data = resp.json()
        
        if 'recordings' in data and len(data['recordings']) > 0:
            rec = data['recordings'][0]
            print(f"Species: {rec.get('en')}")
            print(f"Family: {rec.get('family', 'NOT FOUND')}")
        else:
            print("No recordings found.")
            if 'error' in data:
                print(f"API Error: {data['error']}")
            if 'message' in data:
                print(f"Message: {data['message']}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
