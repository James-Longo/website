import csv
import json
import os

CSV_FILE = 'Clements_v2025-October-2025.csv'
JSON_FILE = 'all_species.json'

def main():
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found.")
        return

    if not os.path.exists(JSON_FILE):
        print(f"Error: {JSON_FILE} not found.")
        return

    # Load CSV and build mapping
    sci_to_family = {}
    print("Reading CSV...")
    import re
    fam_pattern = re.compile(r"^([A-Za-z]+)\s\((.+)\)$")

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        # Identify indices
        try:
            sci_idx = header.index('scientific name')
            fam_idx = header.index('family')
            cat_idx = header.index('category')
        except ValueError as e:
            print(f"Error parsing header: {e}")
            return

        for row in reader:
            if not row: continue
            
            scientific_name = row[sci_idx].strip()
            family_raw = row[fam_idx].strip()
            
            # Format family: "Sci (Eng)" -> "Eng (Sci)"
            match = fam_pattern.match(family_raw)
            if match:
                family_fmt = f"{match.group(2)} ({match.group(1)})"
            else:
                family_fmt = family_raw

            if scientific_name and family_fmt:
                sci_to_family[scientific_name] = family_fmt

    print(f"Loaded {len(sci_to_family)} family mappings.")

    # Load JSON
    print("Reading JSON...")
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        species_list = json.load(f)

    # Update JSON
    updated_count = 0
    for sp in species_list:
        sci = sp.get('sci')
        if sci in sci_to_family:
            sp['family'] = sci_to_family[sci]
            updated_count += 1
        else:
            # Fallback: try lookups? 
            # Sometimes XC names differ slightly from Clements (synonyms)
            # But for now, direct match is fine.
            pass

    print(f"Updated {updated_count} species with family data.")

    # Save JSON
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(species_list, f, ensure_ascii=False, indent=2)
    print("Saved updated species list.")

if __name__ == "__main__":
    main()
