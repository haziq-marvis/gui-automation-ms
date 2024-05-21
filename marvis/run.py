from user_workflow_transformer import transform_workflow_data
import requests


def fetch_workflow(api_url="", token=""):
    base_url = "https://marvis-be-14bb859cfc10.herokuapp.com"
    api_url = base_url + "/user/actions/workflow-format"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE2MzAzNTQxLCJpYXQiOjE3MTYyOTI3NDEsImp0aSI6IjY2NTg0MjEzNjZmYjRlMTI4YTQxMTRlOWY2YmUxODZhIiwidXNlcl9pZCI6Nzl9.J0FKOVH4g5xe75g-pIzYIE-PmEbHOTDL8Ne46Z7N0Xk"
    """Fetch workflow data from the API and transform it."""
    headers = {
        'Authorization': f'Bearer {token}'
    }
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the workflow data: {e}")
        return []


if __name__ == "__main__":
    workflow_data = fetch_workflow()


    for i, workflow in enumerate(workflow_data, start=1):
        print(f"Workflow {i}:")
        print(workflow)
        print()
