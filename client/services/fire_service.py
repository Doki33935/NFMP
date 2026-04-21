class FireService:
    def __init__(self, api):
        self.api = api

    def get_fires(self, status):
        data = self.api.get_fires(status=status)

        # 👉 если DTO используешь
        return data