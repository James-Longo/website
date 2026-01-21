import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use the long name identified in the directory
            client_secret_file = 'client_secret_722232207821-h2mi4lm1aqascpqtp9h4kpn78l475e76.apps.googleusercontent.com.json'
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            # Use run_local_server. It will print a URL if it can't open a browser.
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    folder_id = '1bpY-hrj6KupzaCNnGrLg0tpA3bmL6ynr'
    query = f"'{folder_id}' in parents and trashed = false"
    
    all_files = []
    page_token = None
    
    print("Fetching file list from Google Drive...")
    while True:
        results = service.files().list(
            q=query, 
            pageSize=1000, 
            fields="nextPageToken, files(id, name, webViewLink, webContentLink)",
            pageToken=page_token
        ).execute()
        
        items = results.get('files', [])
        all_files.extend(items)
        
        page_token = results.get('nextPageToken')
        if not page_token:
            break

    if not all_files:
        print('No files found.')
    else:
        print(f'Found {len(all_files)} files.')
        # Save to JSON
        with open('all_files.json', 'w') as f:
            json.dump(all_files, f, indent=2)
        print('Saved to all_files.json')
        
        print('\nSample filenames (first 10):')
        for item in all_files[:10]:
            print(f"- {item['name']}")

if __name__ == '__main__':
    main()
