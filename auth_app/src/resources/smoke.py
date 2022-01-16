from flask_restful import Resource

from src import limiter


class Smoke(Resource):
    decorators = [limiter.limit("3/day")]

    def get(self):
        """
        Server health check
        ---
        tags:
          - smoke
        responses:
          200:
            description: health check
            schema:
              properties:
                message:
                  type: string
        """
        return {"message": "OK"}
