"""
FoodFresh AI - Automated Dataset Download & Setup Script

Downloads the complete 1.16 GB FoodFresh AI dataset archive (data.zip) from the official
GitHub Release asset, verifies its SHA-256 checksum, and extracts it into the project data/ directory.
"""

import argparse
import hashlib
import os
from pathlib import Path
import shutil
import sys
import time
import urllib.request
import zipfile

# Official GitHub Release Asset configuration
RELEASE_TAG = "v1.0.0-data"
ASSET_NAME = "data.zip"
RELEASE_URL = f"https://github.com/anushka326/FoodFreshAI/releases/download/{RELEASE_TAG}/{ASSET_NAME}"
EXPECTED_SHA256 = "dffbb071227a40c20d140a6a60c38872947ed5ec8ce9b3158338474816a145b2"
EXPECTED_SIZE_BYTES = 1218547758  # 1.16 GB

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
AGRIFRESHNET_DIR = RAW_DIR / "AgriFreshNET Freshness and Shelf-Life Image Datase"
FRUITS360_DIR = RAW_DIR / "fruits-360-100x100-main"
DEFAULT_ZIP_PATH = PROJECT_ROOT / "data.zip"


def compute_sha256(filepath: Path, buffer_size: int = 8 * 1024 * 1024) -> str:
    """Compute the SHA-256 checksum of a file with progress updates."""
    hasher = hashlib.sha256()
    total_size = filepath.stat().st_size
    bytes_read = 0
    start_time = time.time()
    last_print = 0

    print(f"Verifying SHA-256 for {filepath.name} ({total_size / (1024 * 1024):.2f} MB)...")
    with open(filepath, "rb") as f:
        while chunk := f.read(buffer_size):
            hasher.update(chunk)
            bytes_read += len(chunk)
            now = time.time()
            if now - last_print >= 1.0 or bytes_read == total_size:
                pct = (bytes_read / total_size) * 100
                speed = (bytes_read / (1024 * 1024)) / (now - start_time) if now > start_time else 0
                print(f"  Checksum calculation: {pct:5.1f}% ({speed:.1f} MB/s)", end="\r", flush=True)
                last_print = now
    print("\n  Checksum calculation complete.")
    return hasher.hexdigest().lower()


def check_existing_dataset(quick: bool = True) -> bool:
    """Check if the full raw dataset is already extracted and valid."""
    if AGRIFRESHNET_DIR.exists() and FRUITS360_DIR.exists():
        if quick:
            # Fast verification: verify key directories exist and contain files
            agri_processed = AGRIFRESHNET_DIR / "Processed Data" / "Processed Data"
            fruits_train = FRUITS360_DIR / "Training"
            if (agri_processed.exists() and any(agri_processed.iterdir()) and
                fruits_train.exists() and any(fruits_train.iterdir())):
                print(f"[OK] Full raw dataset already detected:")
                print(f"  - AgriFreshNET: verified at {AGRIFRESHNET_DIR.relative_to(PROJECT_ROOT)}")
                print(f"  - Fruits-360:   verified at {FRUITS360_DIR.relative_to(PROJECT_ROOT)}")
                return True
        else:
            agri_files = sum(1 for _ in AGRIFRESHNET_DIR.rglob("*") if _.is_file())
            fruits_files = sum(1 for _ in FRUITS360_DIR.rglob("*") if _.is_file())
            if agri_files > 1000 and fruits_files > 1000:
                print(f"[OK] Full raw dataset already detected:")
                print(f"  - AgriFreshNET: {agri_files:,} images at {AGRIFRESHNET_DIR.relative_to(PROJECT_ROOT)}")
                print(f"  - Fruits-360:   {fruits_files:,} images at {FRUITS360_DIR.relative_to(PROJECT_ROOT)}")
                return True
    return False


def download_with_progress(url: str, destination: Path, expected_size: int):
    """Download a file with streaming progress bar and resume/temp file safety."""
    temp_destination = destination.with_suffix(".download")
    print(f"\nDownloading dataset archive from:")
    print(f"  {url}")
    print(f"Target: {destination} ({expected_size / (1024 * 1024):.2f} MB)\n")

    # If partial download exists, start fresh to prevent corruption
    if temp_destination.exists():
        temp_destination.unlink()

    headers = {"User-Agent": "FoodFreshAI-Dataset-Downloader"}
    req = urllib.request.Request(url, headers=headers)

    start_time = time.time()
    downloaded_bytes = 0
    last_print = 0

    try:
        with urllib.request.urlopen(req) as response, open(temp_destination, "wb") as out_file:
            content_length = response.headers.get("Content-Length")
            total_size = int(content_length) if content_length else expected_size

            while True:
                chunk = response.read(1024 * 1024)  # 1 MB chunk
                if not chunk:
                    break
                out_file.write(chunk)
                downloaded_bytes += len(chunk)

                now = time.time()
                if now - last_print >= 1.0 or downloaded_bytes == total_size:
                    pct = (downloaded_bytes / total_size) * 100
                    elapsed = now - start_time
                    speed_mb = (downloaded_bytes / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                    print(
                        f"  Progress: {pct:5.1f}% [{downloaded_bytes / (1024 * 1024):7.1f} / {total_size / (1024 * 1024):.1f} MB] ({speed_mb:5.2f} MB/s)",
                        end="\r",
                        flush=True,
                    )
                    last_print = now

        print("\n[OK] Download finished successfully.")
        temp_destination.replace(destination)
    except KeyboardInterrupt:
        print("\n\n[WARNING] Download interrupted by user.")
        if temp_destination.exists():
            print(f"Partial download saved at: {temp_destination}")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n[ERROR] Download failed: {e}")
        if temp_destination.exists():
            temp_destination.unlink()
        sys.exit(1)


def extract_archive(zip_path: Path, target_dir: Path, force: bool = False):
    """Safely extract the dataset archive preserving directory structure."""
    print(f"\nExtracting {zip_path.name} into {target_dir}...")
    if not force and check_existing_dataset():
        print("Dataset already extracted. Use --force to re-extract.")
        return

    start_time = time.time()
    with zipfile.ZipFile(zip_path, "r") as zf:
        infolist = zf.infolist()
        total_files = len(infolist)
        print(f"Total entries in archive: {total_files:,}")

        extracted_count = 0
        last_print = 0
        # Target extraction directory is project root because zip contains 'data/...'
        extract_root = PROJECT_ROOT

        for member in infolist:
            zf.extract(member, extract_root)
            extracted_count += 1
            now = time.time()
            if now - last_print >= 1.5 or extracted_count == total_files:
                pct = (extracted_count / total_files) * 100
                print(f"  Extracting: {pct:5.1f}% ({extracted_count:,} / {total_files:,} entries)", end="\r", flush=True)
                last_print = now

    elapsed = time.time() - start_time
    print(f"\n[OK] Extraction completed in {elapsed:.1f}s.")


def main():
    parser = argparse.ArgumentParser(description="Download and set up the complete FoodFresh AI dataset.")
    parser.add_argument("--force", action="store_true", help="Force download and extraction even if files already exist.")
    parser.add_argument("--skip-extract", action="store_true", help="Only download and verify the zip archive without extracting.")
    parser.add_argument("--keep-zip", action="store_true", default=True, help="Retain data.zip after extraction.")
    parser.add_argument("--zip-path", type=Path, default=DEFAULT_ZIP_PATH, help="Custom path for data.zip.")
    args = parser.parse_args()

    print("=" * 70)
    print(" FoodFresh AI — Dataset Setup & Download Manager")
    print("=" * 70)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Release asset URL: {RELEASE_URL}")
    print(f"Expected archive size: {EXPECTED_SIZE_BYTES / (1024 * 1024):.2f} MB")
    print(f"Expected SHA-256: {EXPECTED_SHA256}")
    print("=" * 70)

    zip_file = args.zip_path

    # Step 1: Check if already extracted
    if not args.force and check_existing_dataset():
        print("\nAll datasets are present and verified. No download needed.")
        print("To force re-downloading or re-extraction, run with --force.")
        sys.exit(0)

    # Step 2: Check if valid zip archive already exists locally
    need_download = True
    if zip_file.exists() and not args.force:
        actual_size = zip_file.stat().st_size
        if actual_size == EXPECTED_SIZE_BYTES:
            print(f"\nFound existing archive: {zip_file} ({actual_size / (1024 * 1024):.2f} MB)")
            actual_checksum = compute_sha256(zip_file)
            if actual_checksum == EXPECTED_SHA256:
                print(f"[OK] SHA-256 checksum match: {actual_checksum}")
                need_download = False
            else:
                print(f"[WARNING] Checksum mismatch. Expected {EXPECTED_SHA256}, got {actual_checksum}.")
                print("Re-downloading clean archive...")
        else:
            print(f"[WARNING] Local file size ({actual_size} bytes) does not match expected ({EXPECTED_SIZE_BYTES} bytes).")
            print("Re-downloading...")

    # Step 3: Download if necessary
    if need_download:
        download_with_progress(RELEASE_URL, zip_file, EXPECTED_SIZE_BYTES)
        # Verify downloaded file
        actual_checksum = compute_sha256(zip_file)
        if actual_checksum != EXPECTED_SHA256:
            print(f"\n[FATAL] Checksum verification failed after download!")
            print(f"  Expected: {EXPECTED_SHA256}")
            print(f"  Actual:   {actual_checksum}")
            print("The downloaded file may be corrupted. Please run again.")
            sys.exit(1)
        print(f"[OK] Checksum verified: {actual_checksum}")

    # Step 4: Extract
    if not args.skip_extract:
        extract_archive(zip_file, DATA_DIR, force=args.force)

    print("\n" + "=" * 70)
    print(" Dataset Setup Complete!")
    print("=" * 70)
    print("You can now train or evaluate FoodFresh AI models with:")
    print("  python scripts/validate_all_datasets.py")
    print("=" * 70)


if __name__ == "__main__":
    main()
