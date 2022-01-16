from flask import g
from gevent import monkey
from gevent.pywsgi import WSGIServer

from src import create_app

monkey.patch_all()
app = create_app()


@app.teardown_appcontext
def teardown_db(exception):
    g.pop("jwt_redis_blocklist", None)


if __name__ == "__main__":
    http_server = WSGIServer(("", 5000), app)
    http_server.serve_forever()
