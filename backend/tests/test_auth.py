import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import create_app

HEADERS={'X-Requested-With':'Puntuador'}
PASSWORD='test-password-long-enough'

class AuthTests(unittest.TestCase):
    def test_invitation_ownership_session_and_settings(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'AUTH_ENABLED':'1','ADMIN_USERNAME':'owner','ADMIN_PASSWORD':PASSWORD}):
            with TestClient(create_app(Path(directory)/'test.sqlite')) as admin:
                self.assertEqual(admin.get('/api/state').status_code,401)
                self.assertEqual(admin.post('/api/auth/login',json={'username':'owner','password':PASSWORD}).status_code,403)
                login=admin.post('/api/auth/login',headers=HEADERS,json={'username':'owner','password':PASSWORD})
                self.assertEqual(login.status_code,200,login.text)
                self.assertIn('HttpOnly',login.headers['set-cookie'])
                state=admin.get('/api/state').json()
                original=state['active_profile_id']
                invitation=admin.post('/api/auth/invitations',headers=HEADERS).json()['invitation']
                admin_cookie=admin.cookies.get('puntuador_session')
                registered=admin.post('/api/auth/register',headers=HEADERS,json={'username':'friend','password':PASSWORD,'invitation':invitation})
                self.assertEqual(registered.status_code,200,registered.text)
                friend=admin.get('/api/state').json()
                pid=friend['active_profile_id']
                self.assertNotEqual(pid,original)
                self.assertEqual(len(friend['profiles']),1)
                self.assertEqual(admin.get('/api/state',headers={'X-Profile-Id':str(original)}).status_code,404)
                self.assertEqual(admin.post(f'/api/profiles/{original}',headers=HEADERS,json={'name':'hacked','color':'#008cff'}).status_code,404)
                self.assertEqual(admin.delete(f'/api/profiles/{original}',headers=HEADERS).status_code,404)
                self.assertEqual(admin.delete(f'/api/profiles/{pid}',headers=HEADERS).status_code,409)
                self.assertEqual(admin.post('/api/auth/invitations',headers=HEADERS).status_code,403)
                self.assertEqual(admin.post('/api/auth/register',headers=HEADERS,json={'username':'another','password':PASSWORD,'invitation':invitation}).status_code,400)
                self.assertEqual(admin.post('/api/profiles',headers={**HEADERS,'Origin':'https://evil.example'},json={'name':'bad','color':'#008cff'}).status_code,403)
                settings={**friend['settings'],'name':'Friends settings'}
                self.assertEqual(admin.post('/api/settings',headers=HEADERS,json=settings).status_code,200)
                friend_cookie=admin.cookies.get('puntuador_session')
                admin.post('/api/auth/logout',headers=HEADERS)
                admin.cookies.set('puntuador_session',friend_cookie)
                self.assertEqual(admin.get('/api/state').status_code,401)
                admin.cookies.clear();admin.cookies.set('puntuador_session',admin_cookie)
                self.assertEqual(admin.get('/api/state').status_code,401)
                admin.cookies.clear()
                admin.post('/api/auth/login',headers=HEADERS,json={'username':'owner','password':PASSWORD})
                self.assertNotEqual(admin.get('/api/state').json()['settings']['name'],'Friends settings')

    def test_production_requires_credentials_and_serves_build(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'APP_ENV':'production','ADMIN_USERNAME':'owner','ADMIN_PASSWORD':PASSWORD}):
            static=Path(directory)/'dist'
            static.mkdir()
            (static/'index.html').write_text('<html>Puntuador</html>',encoding='utf-8')
            with patch.dict(os.environ, {'FRONTEND_DIST':str(static)}):
                application=create_app(Path(directory)/'test.sqlite')
            with TestClient(application,base_url='https://testserver') as client:
                self.assertEqual(client.get('/').status_code,200)
                response=client.post('/api/auth/login',headers=HEADERS,json={'username':'owner','password':PASSWORD})
                self.assertIn('Secure',response.headers['set-cookie'])
                self.assertEqual(client.get('/api/state').status_code,200)
                self.assertEqual(client.get('/api/unknown').status_code,404)
                self.assertEqual(client.get('/docs').status_code,404)
                self.assertEqual(client.get('/../backend/data/club.sqlite').status_code,404)

    def test_throttle_password_change_and_persistent_auth(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'test.sqlite'
            with patch.dict(os.environ, {'AUTH_ENABLED':'1','ADMIN_USERNAME':'owner','ADMIN_PASSWORD':PASSWORD}):
                with TestClient(create_app(path)) as client:
                    for _ in range(10):
                        self.assertEqual(client.post('/api/auth/login',headers=HEADERS,json={'username':'missing','password':PASSWORD}).status_code,401)
                    self.assertEqual(client.post('/api/auth/login',headers=HEADERS,json={'username':'missing','password':PASSWORD}).status_code,429)
                    client.post('/api/auth/login',headers=HEADERS,json={'username':'owner','password':PASSWORD})
                    old=client.cookies.get('puntuador_session')
                    self.assertEqual(client.post('/api/auth/password',headers=HEADERS,json={'current_password':PASSWORD,'new_password':PASSWORD+'-new'}).status_code,200)
                    client.cookies.clear();client.cookies.set('puntuador_session',old)
                    self.assertEqual(client.get('/api/state').status_code,401)
                    client.cookies.clear()
                    self.assertEqual(client.post('/api/auth/login',headers=HEADERS,json={'username':'owner','password':PASSWORD}).status_code,401)
                    self.assertEqual(client.post('/api/auth/login',headers=HEADERS,json={'username':'owner','password':PASSWORD+'-new'}).status_code,200)
            with patch.dict(os.environ, {'AUTH_ENABLED':'0','APP_ENV':'development'}):
                with TestClient(create_app(path)) as client:
                    self.assertTrue(client.get('/api/auth/me').json()['enabled'])
                    self.assertEqual(client.get('/api/state').status_code,401)

    def test_missing_bootstrap_credentials_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict(os.environ, {'AUTH_ENABLED':'1','ADMIN_USERNAME':'','ADMIN_PASSWORD':''}):
            with self.assertRaises(RuntimeError):
                with TestClient(create_app(Path(directory)/'test.sqlite')):
                    pass

    def test_expired_invitation_and_legacy_profiles(self):
        from app.database import Database
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'test.sqlite'
            database=Database(path)
            database.initialize()
            with database.connect() as db:
                db.execute("UPDATE profiles SET name='Existing profile'")
            with patch.dict(os.environ, {'AUTH_ENABLED':'1','ADMIN_USERNAME':'owner','ADMIN_PASSWORD':PASSWORD}):
                with TestClient(create_app(path)) as client:
                    client.post('/api/auth/login',headers=HEADERS,json={'username':'owner','password':PASSWORD})
                    self.assertEqual(client.get('/api/state').json()['profiles'][0]['name'],'Existing profile')
                    invitation=client.post('/api/auth/invitations',headers=HEADERS).json()['invitation']
                    with database.connect() as db:
                        db.execute('UPDATE invitations SET expires=0')
                    self.assertEqual(client.post('/api/auth/register',headers=HEADERS,json={'username':'friend','password':PASSWORD,'invitation':invitation}).status_code,400)
