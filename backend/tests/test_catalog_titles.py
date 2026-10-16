import tempfile
import unittest
from pathlib import Path
import httpx
from fastapi.testclient import TestClient
from app.main import create_app
from app.catalog_titles import resolve_title


class CatalogTitleTests(unittest.TestCase):
    def test_localized_titles_share_identity_and_cache(self):
        calls = []
        def provider(request):
            calls.append(str(request.url))
            self.assertEqual(request.url.params['q'], 'The Apothecary Diaries')
            return httpx.Response(200, json=[{'show': {'id': 67017, 'name': 'The Apothecary Diaries', 'premiered': '2023-10-22', 'genres': ['Animation'], 'image': None, 'url': 'https://www.tvmaze.com/shows/67017/the-apothecary-diaries'}}])
        with tempfile.TemporaryDirectory() as temp:
            with TestClient(create_app(Path(temp)/'test.sqlite', httpx.MockTransport(provider))) as client:
                for query in ['Los diarios de la boticaria', '  LOS  DIARIOS de la BOTICARIA ', 'Kusuriya no Hitorigoto', 'boticaria', 'los diarios', 'The Apothecary Diaries']:
                    response = client.get('/api/catalog/search', params={'q': query})
                    self.assertEqual(response.status_code, 200)
                    show = response.json()[0]
                    self.assertEqual(show['catalog_id'], 67017)
                    self.assertEqual(show['title'], 'Los diarios de la boticaria')
                    self.assertEqual(show['original_title'], 'The Apothecary Diaries')
                self.assertEqual(len(calls), 1)
                added = client.post('/api/series', json={**show, 'status':'Viendo'})
                self.assertEqual(added.status_code, 200)
                self.assertEqual(added.json()['series'][0]['catalog_id'], 67017)
        self.assertEqual(resolve_title('Una serie desconocida'), 'Una serie desconocida')
        self.assertEqual(resolve_title('La casa búho'), 'The Owl House')
