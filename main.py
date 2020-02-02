import aiohttp_jinja2
import base64
import logging
import sys

import jinja2
from aiohttp import web

from aiohttp_session import setup as setup_session
from aiohttp_security import (
    setup as setup_security,
    SessionIdentityPolicy)

from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet

from aiohttp_polls.authz import DbAuthorizationPolicy
from aiohttp_polls.db import close_pg, init_pg
from aiohttp_polls.routes import setup_routes
from aiohttp_polls.settings import get_config


async def init_app(argv=None):

    app = web.Application()

    app['config'] = get_config(argv)

    # secret_key must be 32 url-safe base64-encoded bytes
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)

    storage = EncryptedCookieStorage(secret_key, cookie_name='API_SESSION')
    setup_session(app, storage)

    policy = SessionIdentityPolicy()
    setup_security(app, policy, DbAuthorizationPolicy(app))

    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('aiohttp_polls', 'templates'))

    # create db connection on startup, shutdown on exit
    app.on_startup.append(init_pg)
    app.on_cleanup.append(close_pg)

    # setup views and routes
    setup_routes(app)

    return app


def main(argv):
    logging.basicConfig(level=logging.DEBUG)

    app = init_app(argv)

    config = get_config(argv)
    web.run_app(
        app,
        host=config['host'],
        port=config['port']
    )


if __name__ == '__main__':
    main(sys.argv[1:])
