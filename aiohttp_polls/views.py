# views.py
import aiohttp_jinja2

from aiohttp import web
from aiohttp_security import (
    remember, forget, authorized_userid,
    check_permission, check_authorized,
)

from . import db
from .authz import check_credentials


@aiohttp_jinja2.template('index.html')
async def index(request):
    username = await authorized_userid(request)
    if not username:
        return web.HTTPFound('/login')
    async with request.app['db'].acquire() as conn:
        cursor = await conn.execute(db.poll.select())
        polls = await cursor.fetchall()
        return {'polls': polls}


@aiohttp_jinja2.template('poll_form.html')
async def poll(request):
    async with request.app['db'].acquire() as conn:
        poll_id = request.match_info['poll_id']
        try:
            results = await db.get_poll_questions(
                conn,
                poll_id)
        except db.RecordNotFound as e:
            raise web.HTTPNotFound(text=str(e))
        return results


@aiohttp_jinja2.template('results.html')
async def vote(request):
    async with request.app['db'].acquire() as conn:
        poll_id = int(request.match_info['poll_id'])
        answers = await request.post()  # {'question_id': 'choice_id'}

        # getting data for current poll
        poll_data = await db.get_poll_questions(
            conn,
            poll_id
        )

        for q in poll_data['questions']:

            # answer for current question
            answer = answers[str(q['question'].id)]

            # transform choices objects to dicts
            q['choices'] = [dict(ch) for ch in q['choices']]

            # add "right" or "wrong" parameter to choice dict
            for ch in q['choices']:
                if str(ch['id']) == answer and ch['correct']:
                    ch['right'] = True
                elif str(ch['id']) == answer and not ch['correct']:
                    ch['wrong'] = True
        return poll_data


# user registration

@aiohttp_jinja2.template('registration.html')
async def registration_page(request):
    async with request.app['db'].acquire() as conn:
        content = {'registration': True}
        username = await authorized_userid(request)
        if username:
            content['success'] = True
        return content


@aiohttp_jinja2.template('registration.html')
async def registration(request):
    async with request.app['db'].acquire() as conn:
        answers = await request.post()
        answers = dict(answers)
        if answers['gender'] not in ['m', 'f']:
            answers.pop('gender')
        result = await db.create_object(conn, db.user, answers)

        context = {'registration': True}

        if result['errors']:
            context['error_message'] = result['errors']
            return aiohttp_jinja2.render_template(
                request=request,
                context=context,
                template_name='registration.html',
            )

        context['success'] = True
        return context


# authorization views

class LoginView(web.View):
    @aiohttp_jinja2.template('login.html')
    async def get(self):
        return {}

    @aiohttp_jinja2.template('login.html')
    async def post(self):
        async with self.request.app['db'].acquire() as conn:
            response = web.HTTPFound('/')
            form = await self.request.post()
            username = form.get('username')

            verified = await check_credentials(conn, username)
            if verified:
                await remember(self.request, response, username)
                return response

            return web.HTTPUnauthorized(
                body='Invalid username')


async def logout(request):
    await check_authorized(request)
    response = web.Response(
        text='You have been logged out',
        content_type='text/html',
    )
    await forget(request, response)
    return response
