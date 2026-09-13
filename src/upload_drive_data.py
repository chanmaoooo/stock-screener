from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from drive_utils import find_folder, find_file, upload_file


SCOPES = ['https://www.googleapis.com/auth/drive']

ROOT_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = ROOT_DIR / 'token.json'

PRICES_ZIP_PATH = ROOT_DIR / 'data' / 'prices.zip'



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

    prices_zip = find_file(
        service,
        'prices.zip',
        parent_id = stock_data_folder['id'],
    )

    upload_file(
        service,
        PRICES_ZIP_PATH,
        prices_zip['id'],
        'application/zip'
    )
    


if __name__ == '__main__':
    main()
