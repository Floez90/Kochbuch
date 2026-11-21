#!/usr/bin/env python3
"""Synchronisiert Rezept-JSON-Dateien aus einem Google-Drive-Ordner nach ./recipes."""
import io
import json
import os
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


def main() -> None:
    sa_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT_JSON"])
    folder_id = os.environ["GDRIVE_FOLDER_ID"].strip()

    creds = service_account.Credentials.from_service_account_info(sa_info, scopes=SCOPES)
    service = build("drive", "v3", credentials=creds)

    recipes_dir = Path("recipes")
    recipes_dir.mkdir(exist_ok=True)

    query = f"'{folder_id}' in parents and trashed = false and name contains '.json'"
    results = service.files().list(
        q=query,
        fields="files(id, name)",
        pageSize=200,
    ).execute()

    files = results.get("files", [])
    synced = 0

    for f in files:
        name = f["name"]
        if name == "recipes-index.json" or not name.endswith(".json"):
            continue

        request = service.files().get_media(fileId=f["id"])
        buf = io.BytesIO()
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        content = buf.getvalue().decode("utf-8")
        # Validiert, dass nur syntaktisch sauberes JSON übernommen wird
        parsed = json.loads(content)
        target = recipes_dir / name
        target.write_text(json.dumps(parsed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        synced += 1

    print(f"{synced} Rezept-JSON(s) aus Google Drive synchronisiert.")


if __name__ == "__main__":
    main()
