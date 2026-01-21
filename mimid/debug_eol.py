import requests
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_eol(q):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    TIMEOUT = 30
    print(f"--- Testing: {q} ---")
    
    try:
        start = time.time()
        search_url = f"https://eol.org/api/search/1.0.json?q={q}"
        print(f"Step 1 (Search): {search_url}")
        resp = requests.get(search_url, verify=False, headers=headers, timeout=TIMEOUT)
        print(f"Step 1 status: {resp.status_code} in {time.time()-start:.2f}s")
        data = resp.json()
        if not data.get('results'):
            print("No results found.")
            return

        page_id = data['results'][0]['id']
        print(f"Found ID: {page_id}")

        start = time.time()
        pages_url = f"https://eol.org/api/pages/1.0/{page_id}.json"
        params = {'images_per_page': 1, 'videos_per_page': 0, 'details': 'true', 'taxonomy': 'false'}
        print(f"Step 2 (Pages): {pages_url}")
        resp = requests.get(pages_url, params=params, verify=False, headers=headers, timeout=TIMEOUT)
        print(f"Step 2 status: {resp.status_code} in {time.time()-start:.2f}s")
        page_data = resp.json()
        
        if 'dataObjects' in page_data and len(page_data['dataObjects']) > 0:
            obj = page_data['dataObjects'][0]
            print(f"Found image: {obj.get('eolMediaURL')}")
        else:
            print("No media found.")

    except Exception as e:
        print(f"Error: {e}")

test_eol("Turdus migratorius")
