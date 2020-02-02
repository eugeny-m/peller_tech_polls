# routes.py
import pathlib

from .views import index, poll, vote
from . admin import (
    admin_index,
    ChoiceListCreateView,
    PollListCreateView,
    QuestionListCreateView,
)


PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_get('/poll/{poll_id}', poll, name='poll')
    app.router.add_post('/poll/{poll_id}/vote', vote, name='vote')
    app.router.add_get('/admin', admin_index, name='admin')
    app.router.add_view('/admin/poll', PollListCreateView,
                        name=PollListCreateView.list_view_name)
    app.router.add_view('/admin/poll/{id}', PollListCreateView,
                        name=PollListCreateView.detail_view_name)
    app.router.add_view('/admin/question', QuestionListCreateView,
                        name=QuestionListCreateView.list_view_name)
    app.router.add_view('/admin/question/{id}', QuestionListCreateView,
                        name=QuestionListCreateView.detail_view_name)
    app.router.add_view('/admin/choice', ChoiceListCreateView,
                        name=ChoiceListCreateView.list_view_name)
    app.router.add_view('/admin/choice/{id}', ChoiceListCreateView,
                        name=ChoiceListCreateView.detail_view_name)
    setup_static_routes(app)


def setup_static_routes(app):
    app.router.add_static(
        '/static/',
        path=PROJECT_ROOT / 'static',
        name='static'
    )
