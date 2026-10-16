import tempfile
import unittest
from pathlib import Path
import httpx
from fastapi.testclient import TestClient
from app.main import create_app
from app.database import Database

SHOW = {'id': 35073, 'name': 'The Owl House', 'premiered': '2020-01-10', 'genres': ['Animation'], 'summary': '<p>A story</p>', 'image': None, 'url': 'https://www.tvmaze.com/shows/35073/the-owl-house'}
EPISODES = [{'id': 101, 'season': 1, 'number': 1, 'name': 'First', 'summary': '', 'runtime': 22, 'airdate': '2020-01-10', 'image': {'medium': 'https://static.tvmaze.com/uploads/images/medium_landscape/1/2.jpg'}}, {'id': 102, 'season': 1, 'number': 2, 'name': 'Second', 'summary': ''}, {'id': 103, 'season': 2, 'number': 1, 'name': 'Third', 'summary': ''}]

class ApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'club.sqlite'
        self.offline = False
        self.client = TestClient(create_app(self.path, httpx.MockTransport(self.catalog)))
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def catalog(self, request):
        if self.offline: raise httpx.ConnectError('offline', request=request)
        if request.url.path.endswith('/episodes'): return httpx.Response(200, json=EPISODES)
        self.assertEqual(request.url.params['q'], 'The Owl House')
        return httpx.Response(200, json=[{'show': SHOW}])

    def add_series(self):
        show = self.client.get('/api/catalog/search?q=La%20casa%20buho').json()[0]
        result = self.client.post('/api/series', json={**show, 'status': 'Viendo'})
        self.assertEqual(result.status_code, 200, result.text)
        return result.json()['series'][0]['id']

    def test_episode_ratings_single_profile_and_refresh(self):
        series_id = self.add_series()
        path = f'/api/series/{series_id}/episodes'
        episodes = self.client.post(path + '/sync').json()
        self.assertEqual([(e['season'], e['number']) for e in episodes], [(1,1),(1,2),(2,1)])
        for invalid in [0, 1.2, 5.5]:
            self.assertEqual(self.client.post('/api/episode-reviews', json={'episode_id': episodes[0]['id'], 'score': invalid}).status_code, 400)
        for score in [0.5, 1.5, 2, 2.5, 5]:
            result = self.client.post('/api/episode-reviews', json={'episode_id': episodes[0]['id'], 'score': score, 'comment': 'Buen capítulo'})
            self.assertEqual(result.status_code, 200, result.text)
            self.assertEqual(len(result.json()['reviews']), 1)
            self.assertEqual(result.json()['reviews'][0]['score'], score)
        self.client.post('/api/episode-reviews', json={'episode_id': episodes[1]['id'], 'score': 3.5})
        refreshed = self.client.post(path + '/sync').json()
        self.assertEqual(refreshed[0]['id'], episodes[0]['id'])
        self.assertEqual(refreshed[0]['score'], 5)
        self.assertEqual(refreshed[0]['runtime'], 22)
        self.assertEqual(refreshed[0]['airdate'], '2020-01-10')
        self.assertTrue(refreshed[0]['image_url'].startswith('https://static.tvmaze.com/'))
        self.assertEqual(refreshed[0]['metadata_loaded'], 1)
        self.assertIsNone(refreshed[2]['score'])
        self.assertEqual(len(self.client.get('/api/state').json()['profiles']), 1)
        self.assertEqual(self.client.post('/api/profiles', json={'name': 'Otro'}).status_code, 200)
        self.offline = True
        self.assertEqual(self.client.get(path).status_code, 200)
        self.assertEqual(self.client.post(path + '/sync').status_code, 502)
        self.assertEqual(self.client.get(path).json()[0]['score'], 5)
        with TestClient(create_app(self.path)) as second:
            self.assertEqual(len(second.get('/api/state').json()['reviews']), 2)

    def test_manual_episodes_and_invalid_references(self):
        series_id = self.add_series()
        path = f'/api/series/{series_id}/episodes'
        body = {'season': 1, 'number': 1, 'title': 'Mi capítulo'}
        episode_id = self.client.post(path, json=body).json()[0]['id']
        self.client.post('/api/episode-reviews', json={'episode_id': episode_id, 'score': 4})
        self.assertEqual(self.client.post(path, json=body).status_code, 409)
        synced = self.client.post(path + '/sync').json()
        self.assertEqual(synced[0]['id'], episode_id)
        self.assertEqual(synced[0]['score'], 4)
        self.assertEqual(self.client.post('/api/episode-reviews', json={'episode_id': 999, 'score': 3}).status_code, 404)
        self.assertEqual(self.client.get('/api/series/999/episodes').status_code, 404)

    def test_cache_and_settings(self):
        self.add_series()
        self.offline = True
        self.assertEqual(self.client.get('/api/catalog/search?q=La%20casa%20buho').status_code, 200)
        with Database(self.path).connect() as db: db.execute('UPDATE catalog_cache SET updated=0')
        self.assertEqual(self.client.get('/api/catalog/search?q=La%20casa%20buho').headers['X-Catalog-Cache'], 'stale')
        self.assertEqual(self.client.get('/api/catalog/search?q=unknown').status_code, 502)
        self.assertEqual(self.client.get('/api/catalog/search?q=x').status_code, 400)
        self.assertEqual(self.client.post('/api/settings', json={'name': 'Mi espacio', 'accent': '#123456', 'compact': True}).json()['settings']['accent'], '#123456')

    def test_legacy_ratings_are_preserved_not_reinterpreted(self):
        path = Path(self.temp.name) / 'old.sqlite'
        with Database(path).connect() as db:
            db.executescript((Path(__file__).parents[1] / 'app/schema.sql').read_text(encoding='utf-8'))
            db.execute('INSERT INTO series(title,genre,year,status,description,color) VALUES(?,?,?,?,?,?)', ('Existente', 'Drama', 2020, 'Viendo', 'Mis notas', '#102372'))
            db.execute('INSERT INTO profiles(name,color) VALUES(?,?)', ('Amigo', '#FF6600'))
            db.execute('INSERT INTO reviews VALUES(1,1,3.5,?)', ('Mi opinión',))
        with TestClient(create_app(path)) as client:
            state = client.get('/api/state').json()
            self.assertEqual(state['series'][0]['description'], 'Mis notas')
            self.assertEqual(state['reviews'], [])
            with Database(path).connect() as db: self.assertEqual(db.execute('SELECT score FROM reviews').fetchone()[0], 3.5)

if __name__ == '__main__': unittest.main()
