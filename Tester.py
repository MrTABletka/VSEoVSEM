import requests
import json

params = {
    "name" : "bob",
    "des" : "text",
}

params = json.dumps(params)
response = requests.get(url=f"http://127.0.0.1:8000/api/apikey123/get_info_user/bimba2")

print(json.loads(response.content.decode('utf-8')))
