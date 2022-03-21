import os
import shlex
import subprocess
import contextlib
from pathlib import Path
from typing import List, Union, Optional


GPG_KEY_EMAIL = os.getenv("GPG_KEY_EMAIL")
ARCHIVE_DIR = Path("archive/")


def call(
    args: List[Union[str, Path]], *, forward_to: Optional[str] = None
) -> None:
    command = " ".join(map(os.fspath, args))
    print(f">>> [LOG] Running: {command}")

    options = {"shell": True}
    if forward_to:
        options["stdout"] = context = open(forward_to, "wb")
    else:
        context = contextlib.nullcontext()

    with context:
        return subprocess.check_call(command, **options)


def create_key_file() -> None:
    # Create GPG key file.
    call(["gpg", "--armor", "--export"], forward_to="KEY.gpg")


def create_packages() -> None:
    # Create Packages, Packages.gz
    call(
        [
            "dpkg-scanpackages",
            "--multiversion",
            ARCHIVE_DIR,
        ],
        forward_to="Packages",
    )

    call(["gzip", "-k", "-f", "Packages"])


def create_release_files() -> None:
    # Create Release, Release.gpg, InRelease
    call(
        ["apt-ftparchive", "release", ARCHIVE_DIR],
        forward_to="Release",
    )

    for option, target in [
        ("-abs", "Release.gpg"),
        ("--clearsign", "InRelease"),
    ]:
        call(
            [
                "gpg",
                "--default-key",
                GPG_KEY_EMAIL,
                option,
                "-o",
                target,
                "Release",
            ]
        )


def main() -> None:
    create_key_file()
    create_packages()
    create_release_files()


if __name__ == "__main__":
    main()
