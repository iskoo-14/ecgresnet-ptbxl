"""
Download and extract the PTB-XL dataset from Kaggle.

Converted from download-dataset.ipynb (Google Colab notebook).

Usage:
    python download_dataset.py --output-dir /path/to/Dataset

Requirements:
    - A Kaggle account with an API token (kaggle.json), available from
      https://www.kaggle.com/settings -> "Create New Token"
    - `pip install kaggle`

If running in Google Colab, Drive mounting and file upload are handled
automatically. Outside Colab, place your kaggle.json in ~/.kaggle/ first,
or pass --kaggle-json to point to it.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

KAGGLE_DATASET = "khyeh0719/ptb-xl-dataset"
DEFAULT_OUTPUT_DIR = "./Dataset"


def in_colab() -> bool:
    try:
        import google.colab  # noqa: F401
        return True
    except ImportError:
        return False


def mount_drive():
    """Mount Google Drive if running in Colab."""
    from google.colab import drive
    drive.mount("/content/drive")


def setup_kaggle_credentials(kaggle_json: str | None):
    """
    Ensure ~/.kaggle/kaggle.json exists.
    - In Colab: prompts a file upload if kaggle_json is not provided.
    - Outside Colab: copies kaggle_json into place if provided.
    """
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_dir.mkdir(parents=True, exist_ok=True)
    target = kaggle_dir / "kaggle.json"

    if target.exists():
        print(f"Found existing Kaggle credentials at {target}")
    elif kaggle_json:
        shutil.copy(kaggle_json, target)
        print(f"Copied Kaggle credentials from {kaggle_json} to {target}")
    elif in_colab():
        from google.colab import files
        print("Please upload your kaggle.json file:")
        uploaded = files.upload()
        uploaded_name = next(iter(uploaded))
        shutil.copy(uploaded_name, target)
        print(f"Saved uploaded credentials to {target}")
    else:
        raise FileNotFoundError(
            "No kaggle.json found. Pass --kaggle-json /path/to/kaggle.json, "
            "or place it at ~/.kaggle/kaggle.json."
        )

    os.chmod(target, 0o600)


def download_dataset(output_dir: str):
    """Download the PTB-XL dataset zip via the Kaggle CLI."""
    print(f"Downloading dataset '{KAGGLE_DATASET}' from Kaggle...")
    subprocess.run(
        ["kaggle", "datasets", "download", "-d", KAGGLE_DATASET],
        check=True,
    )

    zip_name = KAGGLE_DATASET.split("/")[-1] + ".zip"
    if not Path(zip_name).exists():
        raise FileNotFoundError(f"Expected downloaded file '{zip_name}' not found.")
    return zip_name


def extract_dataset(zip_name: str, output_dir: str):
    """Extract the downloaded zip into output_dir, skipping existing files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"Extracting {zip_name} to {output_path}...")
    # -n: never overwrite existing files (avoids interactive y/n/A/N prompts)
    subprocess.run(
        ["unzip", "-n", zip_name, "-d", str(output_path)],
        check=True,
    )
    print("Done.")


def main():
    parser = argparse.ArgumentParser(description="Download and extract the PTB-XL dataset.")
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to extract the dataset into (default: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--kaggle-json",
        default=None,
        help="Path to your kaggle.json credentials file (not needed if already set up).",
    )
    parser.add_argument(
        "--skip-drive-mount",
        action="store_true",
        help="Skip mounting Google Drive even if running in Colab.",
    )
    args = parser.parse_args()

    if in_colab() and not args.skip_drive_mount:
        mount_drive()

    setup_kaggle_credentials(args.kaggle_json)
    zip_name = download_dataset(args.output_dir)
    extract_dataset(zip_name, args.output_dir)


if __name__ == "__main__":
    main()
