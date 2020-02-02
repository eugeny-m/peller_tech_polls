import aiopg.sa
from sqlalchemy import (
    MetaData, Table, Column, ForeignKey,
    Integer, String, Boolean
)


__all__ = ['poll', 'question', 'choice', 'user']

meta = MetaData()


# Poll table description
poll = Table(
    'poll',
    meta,

    Column('id', Integer, primary_key=True),
    Column('title', String(200), nullable=False),

)


# Question table description
question = Table(
    'question',
    meta,

    Column('id', Integer, primary_key=True),
    Column('question_text', String(200), nullable=False),
    Column(
        'poll_id',
        Integer,
        ForeignKey('poll.id', ondelete='CASCADE'),
        nullable=False,
    ),
)


# Choice table description
choice = Table(
    'choice',
    meta,

    Column('id', Integer, primary_key=True),
    Column('choice_text', String(200), nullable=False),
    Column('correct', Boolean, server_default='f'),
    Column(
        'question_id',
        Integer,
        ForeignKey('question.id', ondelete='CASCADE'),
        nullable=False,
    ),
)


# User table description
user = Table(
    'user',
    meta,

    Column('id', Integer, primary_key=True),
    Column('username', String(200), nullable=False, unique=True),
    Column('gender', String(1), nullable=True),  # m/f/None
    Column('age', Integer, nullable=True),
)


class RecordNotFound(Exception):
    """Requested record in database was not found"""


async def init_pg(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
    )
    app['db'] = engine


async def close_pg(app):
    app['db'].close()
    await app['db'].wait_closed()


async def get_children(conn, parent, parent_field, child):
    result = await conn.execute(
        child.select()
        .where(getattr(child.c, parent_field) == parent.id))
    children = await result.fetchall()
    return children


async def get_poll_questions(conn, poll_id):
    # get poll object
    result = await conn.execute(
        poll.select()
        .where(poll.c.id == poll_id))
    poll_record = await result.first()

    if not poll_record:
        msg = "Poll with id: {} does not exists"
        raise RecordNotFound(msg.format(poll_id))

    return_dict = {
        'poll': poll_record,
        'questions': []
    }

    # get poll questions
    questions = await get_children(conn, poll_record, 'poll_id', question)

    # get choices for questions
    for q_record in questions:
        choices = await get_children(conn, q_record, 'question_id', choice)
        return_dict['questions'].append({
            'question': q_record,
            'choices': choices
        })

    return return_dict


async def get_list(conn, model):
    result = await conn.execute(model.select().order_by(model.c.id.asc()))
    records = await result.fetchall()
    return records


async def get_object(conn, model, obj_id):
    result = await conn.execute(
        model.select()
        .where(model.c.id == obj_id))
    record = await result.first()

    if not record:
        msg = "{} with id: {} does not exists"
        raise RecordNotFound(msg.format(model, obj_id))
    return record


async def create_object(conn, model, data):
    resp = {
        'result': None,
        'errors': None
    }
    try:
        result = await conn.execute(model.insert().values(**data))
        resp['result'] = await result.fetchall()
    except Exception as e:
        resp['errors'] = e
    return resp


async def update_object(conn, model, obj_id, data):
    resp = {
        'result': None,
        'errors': None
    }
    try:
        result = await conn.execute(
            model.update()
            .returning(*model.c)
            .where(model.c.id == obj_id)
            .values(**data))
        resp['result'] = await result.fetchall()
    except Exception as e:
        resp['errors'] = e

    return resp
