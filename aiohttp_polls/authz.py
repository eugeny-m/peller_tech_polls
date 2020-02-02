from aiohttp_security.abc import AbstractAuthorizationPolicy

from . import db


class DbAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, app):
        super().__init__()
        self.app = app

    async def authorized_userid(self, identity):
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        async with self.app['db'].acquire() as conn:
            verified = await check_credentials(conn, identity)
            if verified:
                return identity

    async def permits(self, identity, permission, context=None):
        return True


async def check_credentials(conn, username):
    users = await db.get_list(conn, db.user)
    usernames = [u.username for u in users]
    if username not in usernames:
        return False
    return True
