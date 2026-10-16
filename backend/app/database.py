import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .profile_migration import migrate_profiles

ROOT = Path(__file__).resolve().parents[1]


def default_database():
    legacy = ROOT.parent / 'frontend' / 'data' / 'club.sqlite'
    return Path(os.environ.get('CLUB_DB') or (legacy if legacy.exists() else ROOT / 'data' / 'club.sqlite'))


class Database:
    def __init__(self, path=None):
        self.path = Path(path) if path else default_database()

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA foreign_keys=ON')
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # First Python startup retains a consistent backup of the existing database.
        backup = self.path.with_suffix('.before-python.sqlite')
        if self.path.exists() and not backup.exists():
            with self.connect() as source:
                target = sqlite3.connect(backup)
                try:
                    source.backup(target)
                finally:
                    target.close()
        with self.connect() as db:
            db.executescript((ROOT / 'app' / 'schema.sql').read_text(encoding='utf-8-sig'))
            columns = {row['name'] for row in db.execute('PRAGMA table_info(series)')}
            for name, definition in {
                'catalog_source': "TEXT NOT NULL DEFAULT 'tvmaze'", 'catalog_id': 'INTEGER', 'image_url': "TEXT NOT NULL DEFAULT ''",
                'source_url': "TEXT NOT NULL DEFAULT ''", 'original_title': "TEXT NOT NULL DEFAULT ''",
            }.items():
                if name not in columns:
                    db.execute(f'ALTER TABLE series ADD COLUMN {name} {definition}')
            db.execute('DROP INDEX IF EXISTS series_catalog_id')
            db.execute('CREATE UNIQUE INDEX IF NOT EXISTS series_catalog_identity ON series(catalog_source,catalog_id) WHERE catalog_id IS NOT NULL')
            episode_columns = {row['name'] for row in db.execute('PRAGMA table_info(episodes)')}
            for name, definition in {'image_url': "TEXT NOT NULL DEFAULT ''", 'runtime': 'INTEGER', 'airdate': "TEXT NOT NULL DEFAULT ''", 'metadata_loaded': 'INTEGER NOT NULL DEFAULT 0'}.items():
                if name not in episode_columns:
                    db.execute(f'ALTER TABLE episodes ADD COLUMN {name} {definition}')
            settings = json.loads(db.execute('SELECT value FROM settings WHERE id=1').fetchone()['value'])
            if settings['accent'].lower() == '#c4f563':
                settings['accent'] = '#FF6600'
                db.execute('UPDATE settings SET value=? WHERE id=1', (json.dumps(settings),))
            migrate_profiles(db)
