class RoleService:
    ROLE_NAMES = {
        "dispatcher": "Исполнитель-1 (Диспетчер)",
        "inspector": "Исполнитель-2 (Инспектор)",
        "admin": "Администратор",
        "chief": "Руководитель"
    }

    ROLE_ACTIONS = {
        "dispatcher": ["create_fire"],
        "inspector": ["fire_list"],
        "admin": ["fire_list", "users", "monitoring"],
        "chief": ["monitoring"]
    }

    @classmethod
    def get_role_name(cls, role):
        return cls.ROLE_NAMES.get(role, role)

    @classmethod
    def get_actions(cls, role):
        return cls.ROLE_ACTIONS.get(role, [])