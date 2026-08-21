import requests

try:
    res = requests.get("http://localhost:8000/api/v1/openapi.json")
    print("OpenAPI Status:", res.status_code)
    data = res.json()
    paths = list(data.get("paths", {}).keys())
    print("\n--- Registered API Paths ---")
    for p in sorted(paths):
        if "monitoring" in p:
            print(" ->", p)
except Exception as e:
    print("Error:", e)
