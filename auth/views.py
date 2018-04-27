from time import time
from bson.objectid import ObjectId

from aiohttp import web
from aiohttp_session import get_session

from auth.models import User
from auth.utils import error_json


def redirect(request, router_name):
    url = request.app.router[router_name].url()
    raise web.HTTPFound(url)


def set_session(session, user_id, request):
    session['user'] = str(user_id)
    session['last_visit'] = time()
    redirect(request, 'main')


class Login(web.View):

    async def get(self):
        session = await get_session(self.request)
        if session.get('user'):
            redirect(self.request, 'main')
        return web.Response(text='Please enter login or email')

    async def post(self):
        data = await self.request.post()
        user = User(self.request.app.db, data)
        result = await user.check_user()
        if isinstance(result, dict):
            session = await get_session(self.request)
            set_session(session, str(result['_id']), self.request)
        else:
            return web.Response(content_type='application/json', text=error_json(result))


class SignIn(web.View):

    async def get(self, **kwargs):
        session = await get_session(self.request)
        if session.get('user'):
            redirect(self.request, 'main')
        return web.Response(text='Please enter your data')

    async def post(self, **kwargs):
        data = await self.request.post()
        user = User(self.request.app.db, data)
        result = await user.create_user()
        if isinstance(result, ObjectId):
            session = await get_session(self.request)
            set_session(session, str(result), self.request)
        else:
            return web.Response(content_type='application/json', text=error_json(result))


class SignOut(web.View):

    async def get(self, **kwargs):
        session = await get_session(self.request)
        if session.get('user'):
            del session['user']
            redirect(self.request, 'login')
        else:
            raise web.HTTPForbidden(body=b'Forbidden')