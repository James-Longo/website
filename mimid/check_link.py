import requests

url = "https://drive.google.com/uc?id=108O1E_y741Bal0ACw-_s6sigPnA6GL3b&export=download"
try:
    response = requests.get(url, stream=True, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"URL: {response.url}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"Content-Length: {response.headers.get('Content-Length')}")
    # Print first 200 bytes of content to see if it's HTML or Audio
    snippet = response.raw.read(200)
    print(f"Snippet: {snippet[:50]}")
    if b"<!DOCTYPE html>" in snippet or b"<html" in snippet.lower():
        print("RESULT: This is an HTML page, not an audio file. Likely a login or virus scan warning.")
    else:
        print("RESULT: This looks like a binary file (potentially audio).")
except Exception as e:
    print(f"Error: {e}")
