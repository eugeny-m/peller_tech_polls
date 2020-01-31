# routes.py
import pathlib

from .views import index, poll, vote


PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_get('/', index)
    app.router.add_get('/poll/{poll_id}', poll, name='poll')
    app.router.add_post('/poll/{poll_id}/vote', vote, name='vote')
    setup_static_routes(app)


def setup_static_routes(app):
    app.router.add_static('/static/',
                          path=PROJECT_ROOT / 'static',
                          name='static')
