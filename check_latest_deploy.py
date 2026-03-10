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
    # Let's see the most recent deploy status
    if deploys:
        latest = deploys[0]['deploy']
        print(f"Latest Deploy ID: {latest['id']}")
        print(f"Status: {latest['status']}")
        print(f"Git Message: {latest['commit']['message']}")
        
        # If possible, try to find why it failed if it did
        if latest['status'] == 'build_failed':
            print("\nBuild failed. I need to find the logs.")
    else:
        print("No deploys found.")
else:
    print(f"Error: {resp.status_code}")
    print(resp.text)
