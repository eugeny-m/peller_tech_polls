# views.py
import aiohttp_jinja2
from aiohttp import web

from . import db


@aiohttp_jinja2.template('index.html')
async def index(request):
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
