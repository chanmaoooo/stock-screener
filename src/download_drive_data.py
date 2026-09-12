from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload


SCOPES = ['https://www.googleapis.com/auth/drive']

ROOT_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = ROOT_DIR / 'token.json'

LOCAL_DATA_DIR = ROOT_DIR / 'data'
# LOCAL_MASTER_DIR = LOCAL_DATA_DIR / 'master'


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

    stock_data_folder_id = ( stock_data_folder['id'] )

    master_folder = find_folder(
        service,
        'master',
        parent_id = stock_data_folder_id,
    )

    master_folder_id = ( master_folder['id'] )

    master_file = find_file(
        service,
        'master.csv',
        parent_id = master_folder_id,
    )

    master_output_path = (LOCAL_DATA_DIR / 'master' / 'master.csv')

    download_file(
        service,
        master_file['id'],
        master_output_path,
    )

    print(
        f'Downloaded master.csv to '
        f'{master_output_path}'
    )


    prices_zip_file = find_file(
        service,
        'prices.zip',
        parent_id = stock_data_folder_id,
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

