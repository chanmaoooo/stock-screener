from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


SCOPES = ['https://www.googleapis.com/auth/drive']

ROOT_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = ROOT_DIR / 'token.json'

LOCAL_DATA_DIR = ROOT_DIR / 'data'
LOCAL_MASTER_DIR = LOCAL_DATA_DIR / 'master'


def find_file(service, name):
    result = service.files().list(
        q = f"name = '{name}' and trashed = false",
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



def download_file(service, file_id, output_path):
    request = service.files().get_media(
        fileId = file_id
    )

    output_path.parent.mkdir(
        parents = True,
        exist_ok = True,
    )

    with output_path.open('wb') as file:
        downloader = MediaIoBaseDownload(
            file,
            request,
        )

        done = False
        while not done:
            status, done = downloader.next_chunk()

            if status is not None:
                print(
                    f'Download progress: '
                    f'{int(status.progress()*100)}%'
                )



def find_folder(service, name):
    result = service.files().list(
        q = (
            f"name = '{name}' "
            "and mimeType = 'application/vnd.google-apps.folder' "
            "and trashed = false"
        ),
        fields = 'files(id, name)'
    ).execute()

    folders = result.get('files', [])

    if(len(folders)==0):
        raise FileNotFoundError(
            f'Folder not found on Google Drive: {name}'
        )

    if(len(folders)>1):
        raise ValueError(
            f'Multiple folders found with name: {name}'
        )

    return folders[0]



def list_files_in_folder(service, folder_id):
    files = []
    page_token = None

    while True:
        result = service.files().list(
            q = (
                f"'{folder_id}' in parents "
                "and trashed = false"
            ),
            fields = (
                'nextPageToken, '
                'files(id, name)'
            ),
            pageSize = 1000,
            pageToken = page_token,
        ).execute()

        files.extend(
            result.get('files', [])
        )

        page_token = result.get(
            'nextPageToken'
        )

        if page_token is None:
            break

    return files



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

    master_file = find_file(
        service,
        'master.csv',
    )

    output_path = (LOCAL_MASTER_DIR / 'master.csv')

    download_file(
        service,
        master_file['id'],
        output_path,
    )

    print(
        f'Downloaded master.csv to '
        f'{output_path}'
    )


    prices_folder = find_folder(
        service,
        'prices',
    )

    print(
        f"Found prices folder: "
        f"{prices_folder['id']}"
    )

    price_files = list_files_in_folder(
        service,
        prices_folder['id'],
    )

    print(
        f'Found {len(price_files)} files '
        f'in prices folder.'
    )

    for file in price_files[:10]:
        print(
            file['name'],
            file['id'],
        )


    prices_zip_file = find_file(
        service,
        'prices.zip',
    )

    prices_zip_path = (LOCAL_DATA_DIR / 'prices.zip')

    download_file(
        service,
        prices_zip_file['id'],
        prices_zip_path,
    )

    print(
        f'Downloaded prices.zip to '
        f'{prices_zip_path}'
    )





if __name__ == '__main__':
    main()

