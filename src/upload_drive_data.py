import json
import os
from pathlib import Path

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from drive_utils import find_folder, find_file, upload_file


SCOPES = ['https://www.googleapis.com/auth/drive']

ROOT_DIR = Path(__file__).resolve().parent.parent

PRICES_ZIP_PATH = ROOT_DIR / 'data' / 'prices.zip'
FEATURES_PATH = ROOT_DIR / 'data' / 'scores' / 'features.csv'



def main():
    service_account_info = json.loads(
        os.environ['GOOGLE_SERVICE_ACCOUNT_JSON']
    )
        
    credentials = Credentials.from_service_account_info(
        service_account_info,
        scopes = SCOPES,
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

    score_folder = find_folder(
        service,
        'scores',
        parent_id = stock_data_folder['id'],
    )

    features_file = find_file(
        service,
        'features.csv',
        parent_id = score_folder['id'],
    )

    upload_file(
        service,
        FEATURES_PATH,
        features_file['id'],
        'text/csv',
    )


if __name__ == '__main__':
    main()
