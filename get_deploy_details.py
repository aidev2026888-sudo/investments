import requests
import json

headers = {
    "accept": "application/json",
    "authorization": "Bearer rnd_OkUmYpFH0TOFkCfLt6m0UmO4JyeG"
}

service_id = "srv-d6oafkjh46gs73ag7dgg"
deploy_id = "dep-d6oafl3h46gs73ag7dl0"
url = f"https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}"

resp = requests.get(url, headers=headers)
if resp.status_code == 200:
    data = resp.json()
    print(json.dumps(data, indent=2))
else:
    print(f"Error: {resp.status_code}")
    print(resp.text)
