import requests
from models.login import LoginRequestDTO, LoginResponseDTO
from models.fire_create import FireCreateDTO
from models.fire_response import FireResponseDTO
from models.fire_update import FireUpdateDTO 

class ApiClient:
    def __init__(self):
        self.base_url = "http://localhost:8000"

    # =========================
    # AUTH
    # =========================
    def login(self, username, password) -> LoginResponseDTO:
        dto = LoginRequestDTO(username, password)
        response = requests.post(
            f"{self.base_url}/login",
            json=dto.to_dict()
        )

        if response.status_code != 200:
            raise Exception(response.text)

        data = response.json()

        return LoginResponseDTO.from_dict(data)
    

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

    def create_fire(self, fire: FireCreateDTO):
        response = requests.post(
            f"{self.base_url}/fires/",
            json=fire.to_dict()
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return FireResponseDTO.from_dict(response.json())

    def get_fires(self, status=None) -> list[FireResponseDTO]:
        params = {}

        if status:
            params["status"] = status

        response = requests.get(
            f"{self.base_url}/fires/",
            params=params
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return [
            FireResponseDTO.from_dict(f)
            for f in response.json()
        ]

    def get_fire(self, fire_id: int) -> FireResponseDTO:
        response = requests.get(f"{self.base_url}/fires/{fire_id}")

        if response.status_code != 200:
            raise Exception(response.text)

        return FireResponseDTO.from_dict(response.json())

    # =========================
    # INSPECTOR UPDATE
    # =========================
    def update_fire(self, fire_id: int, data: FireUpdateDTO):
        response = requests.put(
            f"{self.base_url}/fires/{fire_id}",
            json=data.to_dict()
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
    

    # =========================
    # REFERENCES
    # =========================
    def get_references(self, ref_type):
        response = requests.get(
            f"{self.base_url}/references/{ref_type}"
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()
    
    def get_selsovets(self, municipality_id=None):
        params = {}

        if municipality_id:
            params["municipality_id"] = municipality_id

        response = requests.get(
            f"{self.base_url}/references/selsovets",
            params=params
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()