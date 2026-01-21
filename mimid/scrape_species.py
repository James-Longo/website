import requests
import re
import json
import os

URL = "https://xeno-canto.org/collection/species/all"
OUTPUT_FILE = "all_species.json"

def scrape_species():
    print(f"Fetching {URL}...")
    headers = {'User-Agent': 'Mimid/1.0'}
    try:
        response = requests.get(URL, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch page: {response.status_code}")
            return

        html = response.text
        print(f"Page fetched ({len(html)} bytes). Parsing...")

        # Pattern to capture species URL suffix and Common Name
        # Looking for rows typically like:
        # <tr><td>...<a href='/species/Genus-species'>Common Name</a>... <span class='sci-name'>Scientific Name</span>...</td></tr>
        # But let's be broader first.
        
        # Regex for common name in anchor
        # Handling absolute URL https://xeno-canto.org/species/...
        species_pattern = re.compile(r"<a href=['\"](?:https://xeno-canto.org)?/species/([A-Za-z]+-[a-z]+)['\"]>([^<]+)</a>")
        
        matches = species_pattern.findall(html)
        
        unique_species = set()
        species_list = []

        for sci_slug, common_name in matches:
            # Clean up
            common_name = common_name.strip()
            # Restore scientific name from slug if needed, but we have common name
            scientific_name = sci_slug.replace('-', ' ')
            
            if common_name not in unique_species:
                unique_species.add(common_name)
                species_list.append({
                    "en": common_name,
                    "sci": scientific_name,
                    "id": sci_slug
                })

        print(f"Found {len(species_list)} unique species.")
        
        # Sort by common name
        species_list.sort(key=lambda x: x['en'])

        with open(OUTPUT_FILE, 'w') as f:
            json.dump(species_list, f, indent=2)
            
        print(f"Saved to {OUTPUT_FILE}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scrape_species()
