import requests
import json
import os
import time
import re

# Queries for Mimid family
QUERIES = [
    'gen:Dumetella cnt:"United States" q:A len:10-60',
    'gen:Mimus cnt:"United States" q:A len:10-60',
    'gen:Toxostoma cnt:"United States" q:A len:10-60'
]

HEADERS = {
    'User-Agent': 'MimidApp/1.0 (educational project)'
}

OUTPUT_DIR = 'audio'
DATA_FILE = 'organized_vocalizations.json'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

all_files = []
species_set = set()
types_set = set()

def simplify_type(v_type):
    v_type = v_type.lower()
    # Remove parenthetical text
    v_type = re.sub(r'\([^)]*\)', '', v_type).strip()
    
    if 'alarm' in v_type:
        return 'Alarm Calls'
    if 'call' in v_type:
        return 'Calls'
    if 'song' in v_type or 'dawn' in v_type:
        return 'Song'
    if 'drum' in v_type:
        return 'Drum'
    return v_type.title()

for q in QUERIES:
    print(f"Querying Xeno-Canto: {q}")
    try:
        # Try replace spaces with + and remove www
        q_encoded = q.replace(' ', '+')
        url = f"https://xeno-canto.org/api/2/recordings?query={q_encoded}"
        print(f"Requesting: {url}")
        resp = requests.get(url, headers=HEADERS)
        print(f"URL: {resp.url}")
        
        if resp.status_code != 200:
            print(f"Error {resp.status_code} fetching metadata")
            continue
            
        data = resp.json()
        recordings = data.get('recordings', [])
        print(f"Found {len(recordings)} recordings. Downloading sample...")
        
        # Download a sample to keep it manageable
        for rec in recordings[:10]: # Limit to 10 per query for now
            rec_id = rec['id']
            file_path = os.path.join(OUTPUT_DIR, f"{rec_id}.mp3")
            
            # Download audio
            if not os.path.exists(file_path):
                print(f"Downloading {rec_id}...")
                try:
                    # rec['file'] is the URL
                    aud_resp = requests.get(rec['file'], headers=HEADERS, timeout=30)
                    with open(file_path, 'wb') as f:
                        f.write(aud_resp.content)
                    time.sleep(1) # Be nice to API
                except Exception as e:
                    print(f"Failed to download {rec_id}: {e}")
                    continue
            else:
                print(f"Skipping {rec_id} (exists)")

            # Process Metadata
            common_name = rec['en']
            v_type = simplify_type(rec['type'])
            location = rec['cnt']
            
            species_set.add(common_name)
            types_set.add(v_type)
            
            all_files.append({
                "id": rec_id,
                "species": common_name,
                "type": v_type,
                "location": location,
                "filename": f"{rec_id}.mp3" 
            })
            
    except Exception as e:
        print(f"Query failed: {e}")

# Build Final Library
library = {
    "files": all_files,
    "species_list": sorted(list(species_set)),
    "vocalization_types": sorted(list(types_set))
}

with open(DATA_FILE, 'w') as f:
    json.dump(library, f, indent=2)

print(f"Done! Saved {len(all_files)} recordings to {DATA_FILE}")
