from dataclasses import dataclass


@dataclass
class UserCreateDTO:
    username: str
    password: str
    password_confirmation: str
    role: str
    full_name: str

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "password": self.password,
            "password_confirmation": self.password_confirmation,
            "role": self.role,
            "full_name": self.full_name,
        }
