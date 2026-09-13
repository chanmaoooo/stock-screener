from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from drive_utils import find_folder, find_file, download_file



SCOPES = ['https://www.googleapis.com/auth/drive']

ROOT_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = ROOT_DIR / 'token.json'

LOCAL_DATA_DIR = ROOT_DIR / 'data'
# LOCAL_MASTER_DIR = LOCAL_DATA_DIR / 'master'



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

