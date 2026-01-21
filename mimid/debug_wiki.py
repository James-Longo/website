import requests
import json

def fetch_wiki_image(q):
    try:
        headers = {'User-Agent': 'MimidBirdApp/1.0 (james@example.com)'}
        q_wiki = q.replace(' ', '_')
        url = f"https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=thumbnail&pithumbsize=600&titles={q_wiki}&redirects=1"
        print(f"Testing Wiki URL: {url}")
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

print("Result for Turdus migratorius:", fetch_wiki_image("Turdus migratorius"))
print("Result for American Robin:", fetch_wiki_image("American Robin"))
