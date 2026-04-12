import requests


class ApiClient:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.token = None

    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/login",
            json={
                "username": username,
                "password": password
            }
        )

        if response.status_code != 200:
            raise Exception("Login failed")

        data = response.json()
        self.token = data.get("access_token")

        return data
    

    
    def create_user(self, username, password, full_name, role):
        response = requests.post(
            f"{self.base_url}/users",
            params={
                "username": username,
                "password": password,
                "full_name": full_name,
                "role": role
            }
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()