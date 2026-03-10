import requests
import json

headers = {
    "accept": "application/json",
    "authorization": "Bearer rnd_OkUmYpFH0TOFkCfLt6m0UmO4JyeG"
}

service_id = "srv-d6oafkjh46gs73ag7dgg"
url = f"https://api.render.com/v1/services/{service_id}/deploys"

resp = requests.get(url, headers=headers)
if resp.status_code == 200:
    deploys = resp.json()
    print(json.dumps(deploys, indent=2))
else:
    print(f"Error: {resp.status_code}")
    print(resp.text)
