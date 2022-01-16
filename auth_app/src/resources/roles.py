from http import HTTPStatus

from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from src.database.db import session_scope
from src.schemas.roles import RoleSchema
from src.services.auth_service import admin_required
from src.services.roles_service import RoleService


class RolesResource(Resource):
    schema = RoleSchema()
    service = RoleService

    @admin_required
    def get(self, role_id: int = None):
        """
        CRUD for roles, only available for admin
        ---
        tags:
          - roles
        parameters:
         - in: path
           name: role_id
           type: integer
           required: true
        security:
            - bearerAuth: []
        responses:
          200:
            description: Role has been updated.
          404:
            description: Role has not been found.
        """
        if not role_id:
            roles = self.service.fetch_all()
            return {"result": self.schema.dump(roles, many=True)}, HTTPStatus.OK

        role = self.service.fetch(role_id)
        if not role:
            return {"message": "not found"}, HTTPStatus.NOT_FOUND

        return {"result": self.schema.dump(role)}, HTTPStatus.OK

    @admin_required
    def post(self):
        try:
            with session_scope() as session:
                role = self.schema.load(request.json, session=session)
        except ValidationError as e:
            return {"message": str(e)}

        is_created = self.service.create(role)
        if is_created:
            return {"message": "created"}, HTTPStatus.CREATED
        return {"message": "something went wrong"}, HTTPStatus.BAD_REQUEST

    @admin_required
    def put(self, role_id: int):
        """
        CRUD for roles, only available for admin
        ---
        tags:
          - roles
        parameters:
         - in: path
           name: role_id
           type: integer
           required: true
        security:
            - bearerAuth: []
        responses:
          200:
            description: Role has been updated.
          404:
            description: Role has not been found.
        """
        try:
            with session_scope() as session:
                updated_role = self.schema.load(request.json, session=session)
        except ValidationError as e:
            return {"message": str(e)}

        is_updated = self.service.update(role_id, updated_role)
        if is_updated:
            return {"message": "updated"}, HTTPStatus.OK
        return {"message": "not found"}, HTTPStatus.NOT_FOUND

    @admin_required
    def delete(self, role_id: int):
        """
        CRUD for roles, only available for admin
        ---
        tags:
          - roles
        parameters:
         - in: path
           name: role_id
           type: integer
           required: true
        security:
            - bearerAuth: []
        responses:
          204:
            description: Role has been deleted.
          404:
            description: Role has not been found.
        """
        is_deleted = self.service.delete(role_id)
        if is_deleted:
            return {"message": "deleted"}, HTTPStatus.NO_CONTENT
        return {"message": "not found"}, HTTPStatus.NOT_FOUND
