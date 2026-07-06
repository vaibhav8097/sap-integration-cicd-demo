import os
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

CLIENT_ID = os.environ["BTP_CLIENT_ID"]
CLIENT_SECRET = os.environ["BTP_CLIENT_SECRET"]
TOKEN_URL = os.environ["BTP_TOKEN_URL"]
API_URL = os.environ["BTP_API_URL"].rstrip("/")

BACKUP_FOLDER = Path("backup/artifacts")
BACKUP_FOLDER.mkdir(parents=True, exist_ok=True)


def get_token():

    print("Getting OAuth Token...")

    response = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
        timeout=30
    )

    response.raise_for_status()

    return response.json()["access_token"]


def get_packages(headers):

    print("Fetching Integration Packages...")

    url = f"{API_URL}/api/v1/IntegrationPackages"

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()["d"]["results"]


def download_artifacts(headers):

    packages = get_packages(headers)

    print(f"Packages Found : {len(packages)}")

    total = 0

    for package in packages:

        package_id = package["Id"]

        print(f"\nPackage : {package_id}")

        artifact_url = (
            f"{API_URL}/api/v1/"
            f"IntegrationPackages('{package_id}')/"
            "IntegrationDesigntimeArtifacts"
        )

        response = requests.get(
            artifact_url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        artifacts = response.json()["d"]["results"]

        for artifact in artifacts:

            artifact_id = artifact["Id"]

            print(f"Downloading : {artifact_id}")

            download_url = (
                f"{API_URL}/api/v1/"
                f"IntegrationDesigntimeArtifacts"
                f"(Id='{artifact_id}',Version='active')/$value"
            )

            file_response = requests.get(
                download_url,
                headers=headers,
                timeout=60
            )

            file_response.raise_for_status()

            output = BACKUP_FOLDER / f"{artifact_id}.zip"

            output.write_bytes(file_response.content)

            print(f"Saved : {output}")

            total += 1

    print(f"\nDownloaded {total} artifacts.")


def main():

    token = get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    download_artifacts(headers)


if __name__ == "__main__":
    main()