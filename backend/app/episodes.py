from .dashboard import record_activity
import html
import re
import sqlite3
import httpx
from fastapi import HTTPException
from .anime_catalog import fetch_episodes


class Episodes:
    def __init__(self, database, client):
        self.database = database
        self.client = client

    def series(self, series_id, profile_id):
        with self.database.connect() as db:
            row = db.execute('SELECT s.* FROM series s JOIN profile_series ps ON ps.series_id=s.id WHERE s.id=? AND ps.profile_id=?', (series_id, profile_id)).fetchone()
        if not row:
            raise HTTPException(404, 'La serie no existe')
        return dict(row)

    def list(self, series_id, profile_id):
        self.series(series_id, profile_id)
        with self.database.connect() as db:
            return [dict(row) for row in db.execute('SELECT e.*,r.score,r.comment FROM episodes e LEFT JOIN profile_episode_reviews r ON r.episode_id=e.id AND r.profile_id=? WHERE e.series_id=? ORDER BY e.season,e.number', (profile_id, series_id))]

    def sync(self, series_id, profile_id):
        series = self.series(series_id, profile_id)
        if series['catalog_source'] == 'jikan' and series['catalog_id']:
            return self.sync_anime(series, profile_id)
        if not series['catalog_id']:
            return self.list(series_id, profile_id)
        try:
            response = self.client.get(f"https://api.tvmaze.com/shows/{series['catalog_id']}/episodes")
            response.raise_for_status()
            rows = response.json()
            entries = [(series_id, row['id'], row['season'], row['number'], row['name'], html.unescape(re.sub('<[^>]*>', '', row.get('summary') or ''))) for row in rows if row.get('number') and row.get('season')]
        except (httpx.HTTPError, ValueError, TypeError, KeyError) as error:
            raise HTTPException(502, 'No se pudieron cargar los capítulos. Reintenta o agrega uno manualmente.') from error
        with self.database.connect() as db:
            # Keep local IDs stable so refreshing never detaches a saved rating.
            for entry in entries:
                existing = db.execute('SELECT id FROM episodes WHERE catalog_id=?', (entry[1],)).fetchone()
                if existing:
                    db.execute('UPDATE episodes SET title=?,description=? WHERE id=?', (entry[4], entry[5], existing['id']))
                else:
                    db.execute('INSERT INTO episodes(series_id,catalog_id,season,number,title,description) VALUES(?,?,?,?,?,?) ON CONFLICT(series_id,season,number) DO UPDATE SET catalog_id=excluded.catalog_id,title=excluded.title,description=excluded.description', entry)
            for row in rows:
                if row.get('number') and row.get('season'):
                    db.execute('UPDATE episodes SET image_url=?,runtime=?,airdate=?,metadata_loaded=1 WHERE catalog_id=? AND series_id=?', ((row.get('image') or {}).get('medium') or '', row.get('runtime'), row.get('airdate') or '', row['id'], series_id))
        return self.list(series_id, profile_id)

    def add(self, series_id, body, profile_id):
        self.series(series_id, profile_id)
        try:
            with self.database.connect() as db:
                db.execute('INSERT INTO episodes(series_id,season,number,title) VALUES(?,?,?,?)', (series_id, body.season, body.number, body.title))
        except sqlite3.IntegrityError as error:
            raise HTTPException(409, 'Ese capítulo ya existe en la temporada') from error
        return self.list(series_id, profile_id)

    def rate(self, body, profile_id):
        with self.database.connect() as db:
            if not db.execute('SELECT e.id FROM episodes e JOIN profile_series ps ON ps.series_id=e.series_id WHERE e.id=? AND ps.profile_id=?', (body.episode_id, profile_id)).fetchone():
                raise HTTPException(404, 'El capítulo no existe')
            db.execute('INSERT INTO profile_episode_reviews VALUES(?,?,?,?) ON CONFLICT(profile_id,episode_id) DO UPDATE SET score=excluded.score,comment=excluded.comment', (profile_id, body.episode_id, body.score, body.comment))
            series_id = db.execute('SELECT series_id FROM episodes WHERE id=?', (body.episode_id,)).fetchone()['series_id']
            record_activity(db, profile_id, series_id, 'rated', str(body.score))

    def sync_anime(self, series, profile_id):
        try:
            rows = fetch_episodes(self.client, series['catalog_id'])
        except (httpx.HTTPError, ValueError, TypeError, KeyError) as error:
            raise HTTPException(502, 'No se pudieron cargar los capítulos de MyAnimeList. Espera unos segundos y reintenta.') from error
        with self.database.connect() as db:
            for row in rows:
                db.execute("INSERT INTO episodes(series_id,season,number,title,airdate,metadata_loaded) VALUES(?,1,?,?,?,1) ON CONFLICT(series_id,season,number) DO UPDATE SET title=excluded.title,airdate=excluded.airdate,metadata_loaded=1", (series['id'], row['number'], row['title'], row['airdate']))
        return self.list(series['id'], profile_id)
