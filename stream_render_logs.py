import requests
import json
import time

headers = {
    "accept": "application/json",
    "authorization": "Bearer rnd_OkUmYpFH0TOFkCfLt6m0UmO4JyeG"
}

service_id = "srv-d6oafkjh46gs73ag7dgg"
# Render logs are often only available for the live service or current build.
# The API returns a URL to a stream.
url = f"https://api.render.com/v1/services/{service_id}/logs"

resp = requests.get(url, headers=headers, stream=True)
print(f"Status Code: {resp.status_code}")

if resp.status_code == 200:
    print("Reading first 20 lines of logs...")
    count = 0
    for line in resp.iter_lines():
        if line:
            print(line.decode('utf-8'))
            count += 1
        if count >= 20:
            break
else:
    print(f"Error: {resp.status_code}")
    print(resp.text)
