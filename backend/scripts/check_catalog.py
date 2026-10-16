"""Live catalogue check with an isolated temporary database."""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from app.main import create_app

with tempfile.TemporaryDirectory() as folder:
    with TestClient(create_app(Path(folder) / 'check.sqlite')) as client:
        response = client.get('/api/catalog/search', params={'q': 'La casa búho'})
        assert response.status_code == 200, response.text
        show = next(item for item in response.json() if item['catalog_id'] == 35073)
        response = client.post('/api/series', json={**show, 'status': 'Viendo'})
        assert response.status_code == 200, response.text
        series_id = response.json()['series'][0]['id']
        response = client.post(f'/api/series/{series_id}/episodes/sync')
        assert response.status_code == 200, response.text
        episodes = response.json()
        assert len(episodes) > 1
        response = client.post('/api/episode-reviews', json={'episode_id': episodes[0]['id'], 'score': 3.5})
        assert response.status_code == 200, response.text
        assert response.json()['reviews'][0]['score'] == 3.5
        print(f'OK: {len(episodes)} episodes imported; first episode rated 3.5.')
        print('OK: real TVmaze search + Python API + SQLite save (isolated test database).')
