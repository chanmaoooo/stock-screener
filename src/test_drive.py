from pathlib import Path

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/drive']

ROOT_DIR = Path(__file__).resolve().parent.parent
TOKEN_PATH = ROOT_DIR / 'token.json'


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

    result = service.files().list(
        pageSize=10,
        fields='files(id, name)',
    ).execute()

    files = result.get('files', [])

    print(f'Found {len(files)} files.')

    for file in files:
        print(
            file['name'],
            file['id'],
        )


if __name__ == '__main__':
    main()