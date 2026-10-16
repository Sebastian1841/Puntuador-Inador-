import base64
import io
from PIL import Image
import unittest
import test_profiles

class AvatarTests(unittest.TestCase):
    setUp = test_profiles.ProfileTests.setUp
    tearDown = test_profiles.ProfileTests.tearDown
    def picture(self):
        output = io.BytesIO()
        Image.new('RGB', (640, 320), '#ff6600').save(output, format='PNG')
        return 'data:image/png;base64,' + base64.b64encode(output.getvalue()).decode()

    def test_avatar_create_persist_edit_remove(self):
        response = self.client.post('/api/profiles', json={'name': 'Con foto', 'avatar': self.picture(), 'description': 'Mis series favoritas'})
        self.assertEqual(response.status_code, 200)
        pid = response.json()['active_profile_id']
        headers = {'X-Profile-Id': str(pid)}
        def current(client):
            return next(p for p in client.get('/api/state', headers=headers).json()['profiles'] if p['id'] == pid)
        avatar = current(self.client)['avatar']
        with Image.open(io.BytesIO(base64.b64decode(avatar.split(',')[1]))) as image:
            self.assertEqual(image.size, (256, 256))
            self.assertEqual(image.format, 'JPEG')
        from fastapi.testclient import TestClient
        from app.main import create_app
        with TestClient(create_app(self.path)) as restarted:
            self.assertEqual(current(restarted)['avatar'], avatar)
            self.assertEqual(current(restarted)['description'], 'Mis series favoritas')
            self.assertEqual(current(restarted)['series_count'], 0)
        self.client.post('/api/profile', headers=headers, json={'name': 'Nuevo nombre'})
        self.assertEqual(current(self.client)['avatar'], avatar)
        self.client.post('/api/profile', headers=headers, json={'name': 'Sin foto', 'avatar': ''})
        self.assertEqual(current(self.client)['avatar'], '')

    def test_invalid_avatar_leaves_profile_unchanged(self):
        before = self.client.get('/api/state').json()['profiles']
        for avatar in ['data:image/svg+xml;base64,PHN2Zz4=', 'data:image/png;base64,YmFk', 'not-an-image', 'x' * 2_800_001]:
            response = self.client.post('/api/profile', json={'name': 'Invalid', 'avatar': avatar})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(self.client.get('/api/state').json()['profiles'], before)
