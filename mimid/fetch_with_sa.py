import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

def main():
    # Path to the service account key file
    SERVICE_ACCOUNT_FILE = 'mimid-485012-3a0a0e72d986.json'
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    service = build('drive', 'v3', credentials=creds)

    folder_id = '1bpY-hrj6KupzaCNnGrLg0tpA3bmL6ynr'
    # Service account must have access to this folder!
    # If it fails with "File not found", ensure the folder is shared with the 
    # service account's email address.
    query = f"'{folder_id}' in parents and trashed = false"
    
    all_files = []
    page_token = None
    
    print("Fetching file list from Google Drive using Service Account...")
    try:
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
            print('No files found. (Check if folder is shared with service account email)')
        else:
            print(f'Found {len(all_files)} files.')
            # Save to JSON
            with open('all_files.json', 'w') as f:
                json.dump(all_files, f, indent=2)
            print('Saved to all_files.json')
            
            print('\nSample filenames (first 10):')
            for item in all_files[:10]:
                print(f"- {item['name']}")
                
    except Exception as e:
        print(f"An error occurred: {e}")
        print("\nIMPORTANT: Please ensure you have shared the Google Drive folder with the service account email.")
        # Try to extract the email from the service account file
        try:
            with open(SERVICE_ACCOUNT_FILE) as f:
                sa_data = json.load(f)
                print(f"Service Account Email: {sa_data.get('client_email')}")
        except:
            pass

if __name__ == '__main__':
    main()
