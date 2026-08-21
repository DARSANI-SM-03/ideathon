import requests

url = "http://localhost:8000/api/v1/monitoring/agent-status"
try:
    res = requests.get(url, timeout=5)
    print(f"Status Code: {res.status_code}")
    data = res.json()
    print("Connected:", data.get("connected"))
    print("Status Label:", data.get("status_label").encode('ascii', 'ignore').decode('ascii'))
except Exception as e:
    print("Error:", e)
