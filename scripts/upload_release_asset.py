"""
Upload data.zip to GitHub Release v1.0.0-data on anushka326/FoodFreshAI.
"""
import os
import sys
import time
import subprocess
import requests

def get_github_token():
    p = subprocess.Popen(
        ['git', 'credential', 'fill'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, _ = p.communicate(input='protocol=https\nhost=github.com\n\n')
    cred = dict(line.split('=', 1) for line in stdout.splitlines() if '=' in line)
    return cred.get('password')

class ProgressReader:
    def __init__(self, filepath):
        self.f = open(filepath, 'rb')
        self.total_size = os.path.getsize(filepath)
        self.bytes_read = 0
        self.start_time = time.time()
        self.last_print_time = 0

    def read(self, size=-1):
        data = self.f.read(size)
        self.bytes_read += len(data)
        now = time.time()
        # Report every 2 seconds or on complete
        if now - self.last_print_time >= 2.0 or self.bytes_read >= self.total_size:
            pct = (self.bytes_read / self.total_size) * 100
            elapsed = now - self.start_time
            speed_mb = (self.bytes_read / (1024 * 1024)) / elapsed if elapsed > 0 else 0
            uploaded_mb = self.bytes_read / (1024 * 1024)
            total_mb = self.total_size / (1024 * 1024)
            print(f"[{pct:5.1f}%] Uploaded {uploaded_mb:7.1f} / {total_mb:.1f} MB ({speed_mb:5.2f} MB/s)", flush=True)
            self.last_print_time = now
        return data

    def __len__(self):
        return self.total_size

    def close(self):
        self.f.close()

def main():
    token = get_github_token()
    if not token:
        print("ERROR: Could not retrieve GitHub token from git credentials.")
        sys.exit(1)

    repo = "anushka326/FoodFreshAI"
    zip_path = "data.zip"
    if not os.path.exists(zip_path):
        print(f"ERROR: {zip_path} not found.")
        sys.exit(1)

    file_size = os.path.getsize(zip_path)
    print(f"Dataset archive: {zip_path}")
    print(f"Size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'FoodFreshAI-Dataset-Uploader'
    }

    # Fetch release
    r = requests.get(f"https://api.github.com/repos/{repo}/releases/tags/v1.0.0-data", headers=headers)
    if r.status_code != 200:
        print(f"ERROR fetching release: {r.status_code} - {r.text}")
        sys.exit(1)

    release_info = r.json()
    release_id = release_info['id']
    print(f"Found release ID: {release_id} (tag: {release_info.get('tag_name')})")

    # Check existing assets
    existing_assets = release_info.get('assets', [])
    for asset in existing_assets:
        if asset.get('name') == 'data.zip':
            if asset.get('size') == file_size:
                print(f"Asset data.zip is ALREADY uploaded! Download URL: {asset.get('browser_download_url')}")
                return
            else:
                print(f"Found partial/different data.zip asset (id: {asset.get('id')}). Deleting before re-upload...")
                del_r = requests.delete(f"https://api.github.com/repos/{repo}/releases/assets/{asset.get('id')}", headers=headers)
                print("Delete response:", del_r.status_code)

    upload_url = f"https://uploads.github.com/repos/{repo}/releases/{release_id}/assets?name=data.zip"
    upload_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/zip',
        'Content-Length': str(file_size),
        'User-Agent': 'FoodFreshAI-Dataset-Uploader'
    }

    print("\nStarting upload to GitHub Releases...")
    reader = ProgressReader(zip_path)
    try:
        up_resp = requests.post(upload_url, data=reader, headers=upload_headers, timeout=3600)
    finally:
        reader.close()

    print(f"\nUpload response status: {up_resp.status_code}")
    if up_resp.status_code in (201, 200):
        asset_info = up_resp.json()
        print("SUCCESS! Asset uploaded.")
        print(f"Asset ID: {asset_info.get('id')}")
        print(f"Asset Name: {asset_info.get('name')}")
        print(f"Asset Size: {asset_info.get('size')} bytes")
        print(f"Browser Download URL: {asset_info.get('browser_download_url')}")
    else:
        print(f"FAILED: {up_resp.text}")
        sys.exit(1)

if __name__ == '__main__':
    main()
