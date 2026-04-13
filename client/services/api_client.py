import requests


class ApiClient:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.token = None

    # =========================
    # AUTH
    # =========================
    def login(self, username, password):
        response = requests.post(
            f"{self.base_url}/login",
            json={
                "username": username,
                "password": password
            }
        )

        if response.status_code != 200:
            raise Exception(response.text)

        data = response.json()
        self.token = data.get("access_token")
        return data

    # =========================
    # USERS (admin only)
    # =========================
    def create_user(self, username, password, full_name, role):
        response = requests.post(
            f"{self.base_url}/users",
            json={
                "username": username,
                "password": password,
                "full_name": full_name,
                "role": role
            }
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    # =========================
    # FIRES
    # =========================

    def create_fire(self, data):
        response = requests.post(
            f"{self.base_url}/fires/",
            json=data
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    def get_fires(self, status=None):
        params = {}

        if status:
            params["status"] = status

        response = requests.get(
            f"{self.base_url}/fires/",
            params=params
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    def get_fire(self, fire_id):
        response = requests.get(f"{self.base_url}/fires/{fire_id}")

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    # =========================
    # INSPECTOR UPDATE
    # =========================
    def update_fire(self, fire_id, data):
        response = requests.put(
            f"{self.base_url}/fires/{fire_id}",
            json=data
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()

    # =========================
    # INSPECTOR CLOSE (finalize)
    # =========================
    def close_fire(self, fire_id):
        response = requests.post(
            f"{self.base_url}/fires/{fire_id}/close"
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()