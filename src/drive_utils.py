from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload



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



def upload_file(service, local_path, drive_file_id, mimetype):
    media = MediaFileUpload(
        local_path,
        mimetype=mimetype,
        resumable=True,
    )

    updated_file = service.files().update(
        fileId = drive_file_id,
        media_body = media,
        fields = 'id, name, modifiedTime',
    ).execute()

    print(
        f"Updated {updated_file['name']} successfully."
    )
    print(
        f"Modified time: {updated_file['modifiedTime']}"
    )


