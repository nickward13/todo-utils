import requests
from msal import PublicClientApplication
import os

# Replace these values with your app's credentials
CLIENT_ID = os.getenv('DELETE_TASKS_CLIENT_ID')
if not CLIENT_ID:
    raise Exception('DELETE_TASKS_CLIENT_ID environment variable not set')
TENANT_ID = 'common'  # Use 'common' for personal Microsoft accounts

# Authentication endpoint and resource
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
SCOPE = ['Tasks.Read']

# Initialize the MSAL public client
app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

def get_access_token():
    flow = app.initiate_device_flow(scopes=SCOPE)
    if 'user_code' not in flow:
        raise Exception('Failed to create device flow')
    print(flow['message'])

    result = app.acquire_token_by_device_flow(flow)
    if 'access_token' in result:
        return result['access_token']
    else:
        raise Exception('Could not acquire access token')

def list_tasks():
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    endpoint = 'https://graph.microsoft.com/v1.0/me/todo/lists'
    response = requests.get(endpoint, headers=headers)
    if response.status_code == 200:
        task_lists = response.json().get('value', [])
        tasks = []
        for task_list in task_lists:
            list_id = task_list['id']
            list_name = task_list['displayName']
            tasks_endpoint = f'https://graph.microsoft.com/v1.0/me/todo/lists/{list_id}/tasks'
            tasks_response = requests.get(tasks_endpoint, headers=headers)
            if tasks_response.status_code == 200:
                tasks_data = tasks_response.json().get('value', [])
                for task in tasks_data:
                    tasks.append({'id': task['id'], 'name': task['title']})
        return tasks
    else:
        raise Exception(f'Error fetching task lists: {response.status_code} {response.text}')

# Example usage
if __name__ == '__main__':
    tasks = list_tasks()
    for task in tasks:
        print(f"Task ID: {task['id']}, Task Name: {task['name']}")