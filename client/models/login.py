from dataclasses import dataclass


@dataclass
class LoginRequestDTO:
    username: str
    password: str

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "password": self.password,
        }
    

@dataclass
class LoginResponseDTO:
    id: int
    username: str
    role: str
    full_name: str

    @staticmethod
    def from_dict(data: dict):
        return LoginResponseDTO(
            id=data["id"],
            username=data["username"],
            role=data["role"],
            full_name=data["full_name"],
        )