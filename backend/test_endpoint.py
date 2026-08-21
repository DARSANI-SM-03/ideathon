import requests

url = "http://localhost:8000/api/v1/monitoring/update"
payload = {
    "student_id": 1,
    "application_name": "Visual Studio Code",
    "window_title": "studiq / test_endpoint.py",
    "website_url": "github.com",
    "category": "Educational",
    "duration_seconds": 5
}

try:
    response = requests.post(url, json=payload, timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error connecting to backend: {e}")
