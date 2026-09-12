from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/drive']

ROOT_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = ROOT_DIR / 'credentials.json'
TOKEN_PATH = ROOT_DIR / 'token.json'



def main():
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_PATH,
        SCOPES,
    )

    credentials = flow.run_local_server(port=0)

    TOKEN_PATH.write_text(
        credentials.to_json(),
        encoding='utf-8',
    )

    print('Created token.json successfully!')



if __name__ == '__main__':
    main()
