# routes.py
import pathlib

from .views import (index, poll, vote, registration_page, registration,
    LoginView, logout)
from . admin import (
    admin_index,
    ChoiceAdmin,
    PollAdmin,
    QuestionAdmin,
)


PROJECT_ROOT = pathlib.Path(__file__).parent


def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_view('/login', LoginView, name='login')
    app.router.add_view('/logout', logout, name='logout')
    app.router.add_get('/poll/{poll_id}', poll, name='poll')
    app.router.add_post('/poll/{poll_id}/vote', vote, name='vote')
    app.router.add_get('/admin', admin_index, name='admin')
    app.router.add_view('/admin/poll', PollAdmin, name=PollAdmin.list_view_name)
    app.router.add_view('/admin/poll/{id}', PollAdmin, name=PollAdmin.detail_view_name)
    app.router.add_view('/admin/question', QuestionAdmin, name=QuestionAdmin.list_view_name)
    app.router.add_view('/admin/question/{id}', QuestionAdmin, name=QuestionAdmin.detail_view_name)
    app.router.add_view('/admin/choice', ChoiceAdmin, name=ChoiceAdmin.list_view_name)
    app.router.add_view('/admin/choice/{id}', ChoiceAdmin, name=ChoiceAdmin.detail_view_name)
    app.router.add_get('/registration', registration_page, name='registration_page')
    app.router.add_post('/registration', registration, name='registration')
    setup_static_routes(app)


def setup_static_routes(app):
    app.router.add_static(
        '/static/',
        path=PROJECT_ROOT / 'static',
        name='static'
    )
