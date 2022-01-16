from flask import g

from src import create_app

app = create_app()


@app.teardown_appcontext
def teardown_db(exception):
    g.pop("jwt_redis_blocklist", None)


if __name__ == "__main__":
    app.run()
