import os

import requests
from models.login import LoginRequestDTO, LoginResponseDTO
from models.fire_create import FireCreateDTO
from models.fire_response import FireResponseDTO
from models.fire_update import FireUpdateDTO 

class ApiClient:
    def __init__(self):
        self.base_url = os.getenv("NFMP_API_URL", "http://127.0.0.1:8000").rstrip("/")
        self.timeout = 8
        self.session = requests.Session()
        self.session.trust_env = False

    def _check(self, response):
        if 200 <= response.status_code < 300:
            return

        raise Exception(f"HTTP {response.status_code}: {response.text}")

    # =========================
    # AUTH
    # =========================
    def login(self, username, password) -> LoginResponseDTO:
        dto = LoginRequestDTO(username, password)
        response = self.session.post(
            f"{self.base_url}/login",
            json=dto.to_dict(),
            timeout=self.timeout,
        )

        self._check(response)

        data = response.json()

        return LoginResponseDTO.from_dict(data)
    

    # =========================
    # USERS (admin only)
    # =========================
    def create_user(self, username, password, password_confirmation, full_name, role):
        response = self.session.post(
            f"{self.base_url}/users",
            json={
                "username": username,
                "password": password,
                "password_confirmation": password_confirmation,
                "full_name": full_name,
                "role": role
            },
            timeout=self.timeout,
        )

        self._check(response)

        return response.json()

    # =========================
    # FIRES
    # =========================

    def create_fire(self, fire: FireCreateDTO):
        response = self.session.post(
            f"{self.base_url}/fires/",
            json=fire.to_dict(),
            timeout=self.timeout,
        )

        self._check(response)

        return FireResponseDTO.from_dict(response.json())

    def get_fires(self, status=None) -> list[FireResponseDTO]:
        params = {}

        if status:
            params["status"] = status

        response = self.session.get(
            f"{self.base_url}/fires/",
            params=params,
            timeout=self.timeout,
        )

        self._check(response)

        return [
            FireResponseDTO.from_dict(f)
            for f in response.json()
        ]

    def get_fire(self, fire_id: int) -> FireResponseDTO:
        response = self.session.get(
            f"{self.base_url}/fires/{fire_id}",
            timeout=self.timeout,
        )

        self._check(response)

        return FireResponseDTO.from_dict(response.json())

    def take_fire(self, fire_id: int) -> FireResponseDTO:
        response = self.session.post(
            f"{self.base_url}/fires/{fire_id}/take",
            timeout=self.timeout,
        )

        self._check(response)
        return FireResponseDTO.from_dict(response.json())

    # =========================
    # INSPECTOR UPDATE
    # =========================
    def update_fire(self, fire_id: int, data: FireUpdateDTO | dict):
        payload = data.to_dict() if hasattr(data, "to_dict") else data

        response = self.session.put(
            f"{self.base_url}/fires/{fire_id}",
            json=payload,
            timeout=self.timeout,
        )

        self._check(response)

        return response.json()

    # =========================
    # INSPECTOR CLOSE (finalize)
    # =========================
    def close_fire(self, fire_id):
        response = self.session.post(
            f"{self.base_url}/fires/{fire_id}/complete",
            timeout=self.timeout,
        )

        self._check(response)

        return response.json()
    

    # =========================
    # REFERENCES
    # =========================
    def get_references(self, ref_type):
        response = self.session.get(
            f"{self.base_url}/references/{ref_type}",
            timeout=self.timeout,
        )

        self._check(response)

        return response.json()
    
    def get_selsovets(self, municipality_id=None):
        params = {}

        if municipality_id:
            params["municipality_id"] = municipality_id

        response = self.session.get(
            f"{self.base_url}/references/selsovets",
            params=params,
            timeout=self.timeout,
        )

        self._check(response)

        return response.json()
