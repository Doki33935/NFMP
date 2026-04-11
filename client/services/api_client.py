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