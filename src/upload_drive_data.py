from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ['https://www.googleapis.com/auth/drive']

ROOT_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = ROOT_DIR / 'token.json'

PRICES_ZIP_PATH = ROOT_DIR / 'data' / 'prices.zip'



def find_file(service, name):
    result = service.files().list(
        q=(
            f"name = '{name}' "
            "and trashed = false"
        ),
        fields = 'files(id, name)',
    ).execute()

    files = result.get('files', [])

    if(len(files)==0):
        raise FileNotFoundError(
            f'File not found on Google Drive: {name}'
        )

    if(len(files)>1):
        raise ValueError(
            f'Multiple files found with name: {name}'
        )

    return files[0]



def main():
    credentials = Credentials.from_authorized_user_file(
        TOKEN_PATH,
        SCOPES,
    )

    service = build(
        'drive',
        'v3',
        credentials=credentials,
    )

    drive_file = find_file(
        service,
        'prices.zip',
    )

    media = MediaFileUpload(
        PRICES_ZIP_PATH,
        mimetype = 'application/zip',
        resumable = True,
    )

    updated_file = service.files().update(
        fileId = drive_file['id'],
        media_body = media,
        fields = 'id, name, modifiedTime',
    ).execute()

    print(
        f"Updated {updated_file['name']} successfully."
    )
    print(
        f"Modified time: {updated_file['modifiedTime']}"
    )
    


if __name__ == '__main__':
    main()
