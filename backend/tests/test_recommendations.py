import json
import tempfile
import unittest
from pathlib import Path
from app.database import Database
from app.recommendations import recommend


class RecommendationTests(unittest.TestCase):
    def test_offline_candidates_exclude_owned_and_rank_by_profile(self):
        with tempfile.TemporaryDirectory() as folder:
            db = Database(Path(folder) / 'test.sqlite')
            db.initialize()
            entries = [dict(catalog_source='jikan', catalog_id=i, title=title,
                            genre=genre, image_url='https://example.com/poster.jpg')
                       for i, title, genre in [(1, 'Owned', 'Drama'), (2, 'Comedy', 'Comedy'), (3, 'Drama', 'Drama')]]
            with db.connect() as connection:
                connection.execute('INSERT INTO catalog_cache VALUES(?,?,?)', ('test', json.dumps(entries), 0))
            profile = [{**entries[0], 'status': 'Viendo', 'favorite': True}]
            self.assertEqual([s['catalog_id'] for s in recommend(db, profile)], [3, 2])
            self.assertEqual(len(recommend(db, [])), 3)
