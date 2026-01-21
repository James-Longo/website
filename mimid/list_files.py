import requests
import re
import json

def list_gdrive_folder(folder_id):
    url = f"https://drive.google.com/embeddedfolderview?id={folder_id}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch folder: {response.status_code}")
        return []
    
    # The data is often embedded in a script tag as a JSON-like structure
    # Look for "folderContents" or similar patterns
    # In the embedded view, it usually has a list of files in a specific format.
    
    # Let's try to extract filenames and IDs using regex
    # Common pattern in GDrive embedded view: ["ID", "Name", Type, ...]
    content = response.text
    # Search for the _initData string which contains the file list in JSON format
    match = re.search(r'_initData\s*=\s*({.*?});', content, re.DOTALL)
    if match:
        data = json.loads(match.group(1))
        # This structure is complex, let's try to find names in it
        # Usually it's deep in "folderContents" or similar
        names = re.findall(r'"([^"]+\.(?:mp3|wav|m4a))"', match.group(1))
        return list(set(names))
    
    # Fallback: search anywhere in content
    filenames = re.findall(r'"([^"]+\.(?:mp3|wav|m4a))"', content)
    
    return list(set(filenames))

if __name__ == "__main__":
    folder_id = "1bpY-hrj6KupzaCNnGrLg0tpA3bmL6ynr"
    files = list_gdrive_folder(folder_id)
    print(f"Found {len(files)} audio files.")
    for f in files[:20]:
        print(f"- {f}")
