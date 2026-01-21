import json
import re

def parse_filename(name):
    """
    Parses filenames like 'Pechora Pipit 01 Song RU-KAM.mp3'
    into {species: 'Pechora Pipit', type: 'Song', id: '01', location: 'RU-KAM'}
    """
    # Remove extension
    base = name.rsplit('.', 1)[0]
    
    # Pattern: [Species] [ID] [Type] [Location]
    # Example: 'Olive-sided Flycatcher 01 Song (Western vocal type) US-CA'
    # The ID is usually 2 digits.
    # The Type can be multiple words (Song, Calls, Alarm calls, Flight calls, etc.)
    # The Location is usually at the end, likely capital letters and a dash.
    
    # Let's try to find the ID first as it's a good separator
    match = re.search(r'\s(\d{2})\s', base)
    if match:
        species = base[:match.start()].strip()
        rest = base[match.end():].strip()
        
        # Now find the location (usually the last part after a space)
        parts = rest.rsplit(' ', 1)
        if len(parts) == 2:
            v_type = parts[0].strip()
            location = parts[1].strip()
        else:
            v_type = rest
            location = "Unknown"
            
        # Clean up: Remove parentheses and content inside
        v_type = re.sub(r'\([^)]*\)', '', v_type).strip()

        # Simplify Vocalization Types
        vt_lower = v_type.lower()
        if "alarm calls" in vt_lower:
            v_type = "Alarm Calls"
        elif "calls" in vt_lower:
            v_type = "Calls"
        elif "song" in vt_lower or "dawn" in vt_lower:
            v_type = "Song"
        elif "drum" in vt_lower:
            v_type = "Drum"
            
        return {
            "species": species,
            "id_num": match.group(1),
            "type": v_type,
            "location": location
        }
    
    return {
        "species": base,
        "id_num": "??",
        "type": "Unknown",
        "location": "Unknown"
    }

def main():
    with open('all_files.json', 'r') as f:
        files = json.load(f)
        
    organized = []
    for f in files:
        if not f['name'].endswith('.mp3'):
            continue
            
        parsed = parse_filename(f['name'])
        organized.append({
            "id": f['id'],
            "name": f['name'],
            "species": parsed['species'],
            "type": parsed['type'],
            "location": parsed['location'],
            "url": f['webContentLink']
        })
        
    # Group by species for the frontend to easily navigate
    library = {}
    for item in organized:
        sp = item['species']
        if sp not in library:
            library[sp] = []
        library[sp].append(item)
        
    all_types = sorted(list(set(item['type'] for item in organized)))

    organized_data = {
        "files": organized,
        "library": library,
        "species_list": sorted(list(library.keys())),
        "vocalization_types": all_types
    }
    
    with open('organized_vocalizations.json', 'w') as f:
        json.dump(organized_data, f, indent=2)
        
    print(f"Organized {len(organized)} vocalizations for {len(library)} species.")
    print("Saved to organized_vocalizations.json")

if __name__ == '__main__':
    main()
