class ReferenceWorker:
    def __init__(self, api):
        self.api = api

    def load_all(self):
        return {
            "forestry": self.api.get_references("forestry"),
            "municipalities": self.api.get_references("municipalities"),
            "participants": self.api.get_references("fire-participants"),
            "tech_types": self.api.get_references("tech-types"),
            "land_types": self.api.get_references("land-types"),
            "reasons": self.api.get_references("reasons"),
        }
