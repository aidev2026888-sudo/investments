import requests
import json

headers = {
    "accept": "application/json",
    "authorization": "Bearer rnd_OkUmYpFH0TOFkCfLt6m0UmO4JyeG"
}

resp = requests.get("https://api.render.com/v1/owners", headers=headers)
if resp.status_code == 200:
    data = resp.json()
    print("Owners:")
    print(json.dumps(data, indent=2))
else:
    print(f"Failed to get owners: {resp.status_code}")
    print(resp.text)
