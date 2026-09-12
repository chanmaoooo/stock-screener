from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ['https://www.googleapis.com/auth/drive']

ROOT_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = ROOT_DIR / 'token.json'

PRICES_ZIP_PATH = ROOT_DIR / 'data' / 'prices.zip'



def find_file(service, name, parent_id=None):
    query_parts = [
        f"name = '{name}'",
        "trashed = false",
    ]

    if parent_id is not None:
        query_parts.append(
            f"'{parent_id}' in parents"
        )

    result = service.files().list(
        q = ' and '.join(query_parts),
        fields = 'files(id, name)',
    ).execute()

    files = result.get('files', [])

    if(len(files)==0):
        raise FileNotFoundError(
            f'File not found: {name}'
        )

    if(len(files)>1):
        raise ValueError(
            f'Multiple files found: {name}'
        )

    return files[0]


def find_folder(service, name, parent_id=None):
    query_parts = [
        f"name = '{name}'",
        "mimeType = 'application/vnd.google-apps.folder'",
        "trashed = false",
    ]

    if parent_id is not None:
        query_parts.append(
            f"'{parent_id}' in parents"
        )

    result = service.files().list(
        q = ' and '.join(query_parts),
        fields = 'files(id, name)'
    ).execute()

    folders = result.get('files', [])

    if(len(folders)==0):
        raise FileNotFoundError(
            f'Folder not found: {name}'
        )

    if(len(folders)>1):
        raise ValueError(
            f'Multiple folders found: {name}'
        )

    return folders[0]



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

    stock_data_folder = find_folder(
        service,
        'stock-screener-data',
    )

    drive_file = find_file(
        service,
        'prices.zip',
        parent_id = stock_data_folder['id'],
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
