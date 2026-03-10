import requests
import json

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer rnd_OkUmYpFH0TOFkCfLt6m0UmO4JyeG"
}

payload = {
    "type": "web_service",
    "name": "investments-dashboard-api",
    "ownerId": "tea-d6o9sbh5pdvs73ee3o60",
    "repo": "https://github.com/aidev2026888-sudo/investments",
    "branch": "master",
    "autoDeploy": "yes",
    "rootDir": "dashboard",
    "serviceDetails": {
        "env": "node",
        "plan": "free",
        "envSpecificDetails": {
            "buildCommand": "npm install && npm run build",
            "startCommand": "npm run start"
        }
    }
}

resp = requests.post("https://api.render.com/v1/services", headers=headers, json=payload)

if resp.status_code in [200, 201]:
    data = resp.json()
    print("Service Created Successfully!")
    print(f"Service ID: {data['service']['id']}")
    print(f"Service URL: {data['service']['serviceDetails']['url']}")
    print(f"Deployment Dashboard: {data['service']['url']}")
else:
    print(f"Error: {resp.status_code}")
    print(json.dumps(resp.json(), indent=2))
