import io
import os
import requests
import zipfile
from argparse import ArgumentParser
from pathlib import Path
from typing import Iterator, Dict, Tuple, Any, IO
from urllib.request import urlretrieve


API_BASE = "https://api.github.com"
TARGET_REPO = "httpie/httpie"

GITHUB_USER = os.getenv("GITHUB_USER")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_AUTH = (GITHUB_USER, GITHUB_TOKEN)

DEFAULT_PATH = Path("archive/")


def iter_releases(repo: str) -> Iterator[Dict[str, Any]]:
    page = 1
    while True:
        response = requests.get(
            API_BASE + f"/repos/{repo}/releases",
            auth=GITHUB_AUTH,
            params={"page": page, "per_page": 100},
        )
        response.raise_for_status()

        data = response.json()
        if data:
            yield from data
        else:
            break

        page += 1


def iter_debian_assets() -> Iterator[Tuple[str, str]]:
    for release in iter_releases(repo=TARGET_REPO):
        for asset in release["assets"]:
            if asset["name"].endswith(".deb"):
                yield release["tag_name"], asset["browser_download_url"]


def collect_assets_to(path: Path) -> None:
    for tag_name, debian_asset in iter_debian_assets():
        with open(path / f"httpie-cli_{tag_name}-0.deb", "wb") as stream:
            response = requests.get(debian_asset)
            stream.write(response.content)


def main():
    parser = ArgumentParser()
    parser.add_argument("--dest", type=Path, default=DEFAULT_PATH)

    options = parser.parse_args()
    options.dest.mkdir(exist_ok=True)

    collect_assets_to(options.dest)


if __name__ == "__main__":
    main()
