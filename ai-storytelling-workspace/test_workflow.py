import requests
import time

print("Creating project...")
proj_res = requests.post("http://localhost:8001/api/projects", json={
    "name": "Test Workflow Novel",
    "description": "A sci-fi novel about AI agents",
    "genre": "Science Fiction",
    "target_audience": "Adult",
    "tone": "Dark",
    "pov": "First Person"
})
print(proj_res.status_code, proj_res.text)
if proj_res.status_code != 200 and proj_res.status_code != 201:
    exit(1)
project_id = proj_res.json()["id"]

print("Starting workflow...")
wf_res = requests.post(f"http://localhost:8001/api/workflow/{project_id}/start", json={})
print(wf_res.status_code, wf_res.text)
workflow_id = wf_res.json()["id"]

print("Polling status...")
for i in range(15):
    time.sleep(2)
    stat_res = requests.get(f"http://localhost:8001/api/workflow/{project_id}/status")
    print(stat_res.json())

