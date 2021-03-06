from time import time

import aiohttp_jinja2
from aiohttp import web
from marshmallow.exceptions import ValidationError

from auth.models import User
from core.utils import error_json, redirect
from core.decorators import login_required, anonymous_required


class AuthView(web.View):

    async def login_user(self, user_id):
        """ Put user to session and redirect to Index """
        self.request.session['user'] = str(user_id)
        self.request.session['time'] = time()
        redirect(self.request, 'main')


class Login(AuthView):
    template_name = 'auth/login.html'
    template_content = 'Please enter login or email'

    @anonymous_required
    @aiohttp_jinja2.template(template_name)
    async def get(self):
        return {'content': self.template_content}

    @anonymous_required
    @aiohttp_jinja2.template(template_name)
    async def post(self):
        data = await self.request.post()
        user = await User.find_one({'login': data.get('login'), 'password': data.get('password')})
        if user:
            await self.login_user(user.id)
        else:
            return {'content': self.template_content, 'error': 'The username or password you entered is incorrect'}


class SignIn(AuthView):
    template_name = 'auth/sign.html'
    template_content = 'Please enter your data'

    @anonymous_required
    @aiohttp_jinja2.template(template_name)
    async def get(self, **kwargs):
        return {'content': self.template_content}

    @anonymous_required
    async def post(self, **kwargs):
        data = await self.request.post()
        try:
            user = User(**data)
            result = await user.commit()
        except ValidationError as e:
            print(e)
            return web.Response(content_type='application/json', text=error_json('Error'))
        else:
            await self.login_user(result.inserted_id)


class Logout(web.View):

    @login_required
    async def get(self, **kwargs):
        self.request.session.pop('user')
        redirect(self.request, 'login')
