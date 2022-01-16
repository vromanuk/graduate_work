from http import HTTPStatus

from flask import jsonify
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                jwt_required)
from flask_restful import Resource


class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """
        Refresh token view.
        ---
        tags:
          - token
        security:
            - bearerAuth: []
        responses:
          200:
            description: User role has been updated.
        """
        identity = get_jwt_identity()
        access_token = create_access_token(identity=identity)
        return jsonify(access_token=access_token), HTTPStatus.OK
