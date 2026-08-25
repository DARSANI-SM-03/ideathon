"""
Direct Verification Test for GET /api/v1/monitoring/installer/download (Native Script Package)
==============================================================================================
"""
import sys
import os

backend_path = os.path.dirname(os.path.abspath(__file__))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.main import app
from fastapi.testclient import TestClient

def test_installer_download_endpoint():
    print("==========================================================")
    print(" TESTING GET /api/v1/monitoring/installer/download ROUTE  ")
    print("==========================================================")

    client = TestClient(app)
    endpoint = "/api/v1/monitoring/installer/download"

    response = client.get(endpoint)
    print(f"HTTP Status Code    : {response.status_code}")
    print(f"Content-Type        : {response.headers.get('content-type')}")
    print(f"Content-Disposition : {response.headers.get('content-disposition')}")
    print(f"Content-Length      : {response.headers.get('content-length')}")
    print(f"Downloaded Size     : {len(response.content)} bytes")

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"
    assert response.headers.get('content-type') == 'application/x-msdos-program'
    assert 'attachment; filename="StudIQAgentSetup.bat"' in response.headers.get('content-disposition', '')
    assert len(response.content) > 10000000, "Downloaded content size should be non-empty setup script"

    # Save to temporary file and check header content
    tmp_path = os.path.join(backend_path, "temp_downloaded_setup.bat")
    with open(tmp_path, "wb") as tmp_file:
        tmp_file.write(response.content)

    print(f"Saved binary to     : {tmp_path}")

    with open(tmp_path, "r", encoding="utf-8", errors="ignore") as f:
        header = f.read(150)
        print(f"Script Header       : {header[:60]}...")
        assert "@echo off" in header, "Script must be a valid Windows batch setup script"
        assert "-----BEGIN PAYLOAD-----" in response.text, "Script must contain embedded payload marker"

    print("==========================================================")
    print(" SUCCESS: Download endpoint returned valid Native Windows Setup Script!")
    print("==========================================================")

if __name__ == "__main__":
    test_installer_download_endpoint()
