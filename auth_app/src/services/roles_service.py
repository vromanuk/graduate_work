from src.database.models import Role


class RoleService:
    model = Role

    @classmethod
    def fetch(cls, role_id: int):
        return cls.model.fetch(role_id)

    @classmethod
    def fetch_all(cls):
        return cls.model.fetch_all()

    @classmethod
    def create(cls, role) -> bool:
        return cls.model.create(role)

    @classmethod
    def update(cls, role_id, updated_role) -> bool:
        return cls.model.update(role_id, updated_role)

    @classmethod
    def delete(cls, role_id: int) -> bool:
        return cls.model.delete(role_id)
