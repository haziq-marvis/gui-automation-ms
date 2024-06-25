from user_workflow_transformer import transform_workflow_data
import requests
from core.driver import assistant
import json

def fetch_workflow(api_url="", token=""):
    base_url = "https://marvis-be-prod-34fd7452eb30.herokuapp.com"
    api_url = base_url + "/user/actions/workflow-format"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE4MzAyNTYxLCJpYXQiOjE3MTgyOTE3NjEsImp0aSI6IjU3MzdjY2U3MjZlOTQyZTM5NmEwYjUzNWViYjUwM2RkIiwidXNlcl9pZCI6NH0.Z22Vc00_xjUur9y5itGSZR9z480GKKhoS91pB3kvuGw"
    """Fetch workflow data from the API and transform it."""
    headers = {
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching thePassword123"
              f" workflow data: {e}")
        return []


if __name__ == "__main__":
    workflow_data = fetch_workflow()
    latest_workflow = workflow_data[0]
    latest_workflow = latest_workflow[list(latest_workflow.keys())[0]]
    print(latest_workflow)
    cleaned_workflow = []
    for step in latest_workflow:
        if step["act"] != "scroll" and step not in cleaned_workflow:
            cleaned_workflow.append(step)
    assistant(assistant_goal="", app_name="Google Chrome",  execute_json_case=json.dumps(latest_workflow), marvis=True)

