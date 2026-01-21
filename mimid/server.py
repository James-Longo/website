from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)
CORS(app)

XC_BASE = "https://xeno-canto.org/api/3/recordings"
XC_TOKEN = "ea1aba0d681aba25fec6c95175559d9c3fbaf7fe"

SPECIES_FILE = 'all_species.json'
SPECIES_LIST = []
SCI_TO_FAMILY = {}

def load_data():
    global SPECIES_LIST, SCI_TO_FAMILY
    if os.path.exists(SPECIES_FILE):
        with open(SPECIES_FILE, 'r', encoding='utf-8') as f:
            SPECIES_LIST = json.load(f)
            # Build lookup map
            SCI_TO_FAMILY = {}
            for s in SPECIES_LIST:
                if 'family' in s:
                    SCI_TO_FAMILY[s['sci']] = s['family']
    print(f"Loaded {len(SPECIES_LIST)} species.")

load_data()

@app.route('/api/debug/reload')
def reload_data():
    load_data()
    return jsonify({"status": "reloaded", "count": len(SPECIES_LIST)})

@app.route('/api/suggest')
def suggest_species():
    query = request.args.get('q', '').lower()
    if len(query) < 2:
        return jsonify([])
    matches = [s for s in SPECIES_LIST if query in s['en'].lower() or query in s['sci'].lower()][:10]
    return jsonify(matches)

@app.route('/api/families')
def get_families():
    families = set()
    for s in SPECIES_LIST:
        if 'family' in s and s['family']:
            families.add(s['family'])
    return jsonify(sorted(list(families)))

@app.route('/api/species_by_family')
def get_species_by_family():
    family_query = request.args.get('family')
    if not family_query:
        return jsonify([])
    matches = [s for s in SPECIES_LIST if s.get('family') == family_query]
    return jsonify(matches)

@app.route('/api/genera')
def get_genera():
    genera = set()
    for s in SPECIES_LIST:
        sci = s.get('sci', '')
        if sci:
            genus = sci.split(' ')[0]
            if genus:
                genera.add(genus)
    return jsonify(sorted(list(genera)))

@app.route('/api/species_by_genus')
def get_species_by_genus():
    genus_query = request.args.get('genus')
    if not genus_query:
        return jsonify([])
    
    matches = []
    for s in SPECIES_LIST:
        sci = s.get('sci', '')
        if sci:
            genus = sci.split(' ')[0]
            if genus == genus_query:
                matches.append(s)
    return jsonify(matches)

import sqlite3
import time
import threading

CACHE_FILE = 'xc_cache.db'
LAST_REQUEST_TIME = 0
rate_lock = threading.Lock()

def init_db():
    with sqlite3.connect(CACHE_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS queries 
                        (query TEXT PRIMARY KEY, response TEXT, timestamp REAL)''')
        conn.execute('''CREATE TABLE IF NOT EXISTS images 
                        (species TEXT PRIMARY KEY, data TEXT, timestamp REAL)''')

init_db()

@app.route('/api/species_image')
def species_image():
    species_sci = request.args.get('name')
    species_en = request.args.get('en')
    if not species_sci:
        return jsonify({"error": "No species name provided"}), 400

    # 1. Check Cache
    try:
        with sqlite3.connect(CACHE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM images WHERE species = ?", (species_sci,))
            row = cursor.fetchone()
            if row:
                return jsonify(json.loads(row[0]))
    except Exception as e:
        print(f"Image cache read error: {e}")

    # Helper for EOL (User's preferred source)
    def fetch_eol_image(q):
        try:
            # Browser-like header helps avoid blocks
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            # Step 1: Search for ID
            search_url = f"https://eol.org/api/search/1.0.json?q={q}"
            r1 = requests.get(search_url, verify=False, headers=headers, timeout=5)
            search_data = r1.json()
            if not search_data.get('results'): return None
            
            page_id = search_data['results'][0]['id']
            # Step 2: Fetch Media for that ID
            pages_url = f"https://eol.org/api/pages/1.0/{page_id}.json"
            params = {'images_per_page': 1, 'videos_per_page': 0, 'details': 'true', 'taxonomy': 'false'}
            r2 = requests.get(pages_url, params=params, verify=False, headers=headers, timeout=5)
            page_data = r2.json()
            
            if 'dataObjects' in page_data and len(page_data['dataObjects']) > 0:
                obj = page_data['dataObjects'][0]
                media_url = obj.get('eolMediaURL') or obj.get('eolThumbnailURL')
                if media_url:
                    return {
                        "url": media_url,
                        "license": obj.get('license', 'CC'),
                        "rightsHolder": obj.get('rightsHolder', 'EOL Contributor'),
                        "source": "EOL"
                    }
        except Exception as e:
            print(f"EOL attempt failed for {q}: {e}")
        return None

    # Helper for Wikipedia (Reliable fallback)
    def fetch_wiki_image(q):
        try:
            headers = {'User-Agent': 'MimidBirdApp/1.0 (james@example.com)'}
            # Wikipedia works best with underscores
            q_wiki = q.replace(' ', '_')
            url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=thumbnail&pithumbsize=600&titles={q_wiki}&redirects=1"
            resp = requests.get(url, headers=headers, timeout=5)
            data = resp.json()
            pages = data.get('query', {}).get('pages', {})
            for pid in pages:
                if 'thumbnail' in pages[pid]:
                    return {
                        "url": pages[pid]['thumbnail']['source'],
                        "license": "Public Domain / CC",
                        "rightsHolder": "Wikipedia Contributors",
                        "source": "Wikipedia"
                    }
        except Exception as e:
            print(f"Wiki attempt failed for {q}: {e}")
        return None

    # Try sources in order of preference
    # Priority: EOL (Sci) -> EOL (En) -> Wiki (Sci) -> Wiki (En)
    image_info = fetch_eol_image(species_sci)
    if not image_info and species_en:
        image_info = fetch_eol_image(species_en)
    
    if not image_info:
        # Fall back to high-reliability Wikipedia
        image_info = fetch_wiki_image(species_sci)
    
    if not image_info and species_en:
        image_info = fetch_wiki_image(species_en)

    if image_info:
        # Cache the success
        try:
            with sqlite3.connect(CACHE_FILE) as conn:
                conn.execute("INSERT OR REPLACE INTO images (species, data, timestamp) VALUES (?, ?, ?)", 
                             (species_sci, json.dumps(image_info), time.time()))
        except Exception as e:
            print(f"Image cache write error: {e}")
        return jsonify(image_info)
    
    return jsonify({"error": "No image found"}), 404

@app.route('/api/search')
def search_xc():
    global LAST_REQUEST_TIME
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    
    # Check Cache FIRST (No rate limit for cache)
    try:
        with sqlite3.connect(CACHE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT response FROM queries WHERE query = ?", (query,))
            row = cursor.fetchone()
            if row:
                print(f"Cache hit for: {query}")
                return jsonify(json.loads(row[0]))
    except Exception as e:
        print(f"Cache read error: {e}")

    # Rate Limiting (1 request per second) - only for XC fetches
    with rate_lock:
        now = time.time()
        wait_time = (LAST_REQUEST_TIME + 1.1) - now
        if wait_time > 0:
            print(f"Rate limiting: sleeping {wait_time:.2f}s")
            time.sleep(wait_time)
        LAST_REQUEST_TIME = time.time()
    
    try:
        # Forward the search to Xeno-Canto API v3
        print(f"Fetching from XC: {query}")
        params = {
            'query': query,
            'key': XC_TOKEN
        }
        resp = requests.get(XC_BASE, params=params)
        
        # Handle non-200 responses gently (don't cache errors if transient?)
        if resp.status_code != 200:
             return jsonify({"error": f"XC Error {resp.status_code}", "details": resp.text}), resp.status_code

        data = resp.json()
        
        # Inject family data if available
        if 'recordings' in data:
            for rec in data['recordings']:
                # XC provides 'gen' and 'sp'
                sci_name = f"{rec.get('gen', '')} {rec.get('sp', '')}".strip()
                if sci_name in SCI_TO_FAMILY:
                    rec['family'] = SCI_TO_FAMILY[sci_name]
        
        # Save to Cache
        try:
             with sqlite3.connect(CACHE_FILE) as conn:
                conn.execute("INSERT OR REPLACE INTO queries (query, response, timestamp) VALUES (?, ?, ?)", 
                             (query, json.dumps(data), time.time()))
        except Exception as e:
            print(f"Cache write error: {e}")
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/proxy/audio')
def proxy_audio():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    
    try:
        # Stream the audio file
        req = requests.get(url, stream=True)
        return Response(stream_with_context(req.iter_content(chunk_size=1024)),
                        content_type=req.headers['content-type'])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
