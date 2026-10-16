from .dashboard import dashboard, record_activity
import json
import sqlite3
from fastapi import HTTPException

class ClubRepository:
    def __init__(self, database, owner_id=None):
        self.database = database
        self.owner_id = owner_id

    def resolve_profile(self, value=None):
        with self.database.connect() as db:
            if value is None:
                row = db.execute('SELECT id FROM profiles WHERE owner_id=? ORDER BY id LIMIT 1', (self.owner_id,)).fetchone() if self.owner_id is not None else db.execute('SELECT id FROM profiles ORDER BY id LIMIT 1').fetchone()
                if not row: raise HTTPException(404, 'No hay perfiles disponibles')
                return row['id']
            try: profile_id = int(value)
            except (ValueError, TypeError): raise HTTPException(400, 'Perfil inválido')
            if not db.execute('SELECT id FROM profiles WHERE id=?', (profile_id,)).fetchone():
                raise HTTPException(404, 'El perfil no existe')
            if self.owner_id is not None and not db.execute('SELECT 1 FROM profiles WHERE id=? AND owner_id=?',(profile_id,self.owner_id)).fetchone():
                raise HTTPException(404, 'El perfil no existe')
            return profile_id

    def state(self, profile_id=None):
        profile_id = self.resolve_profile(profile_id)
        with self.database.connect() as db:
            series = [dict(row) for row in db.execute('''
                SELECT s.*,COALESCE(ps.status,'Pendiente') AS personal_status,COALESCE(ps.favorite,0) AS favorite,
                (SELECT COUNT(*) FROM episodes e WHERE e.series_id=s.id) AS episode_count
                FROM series s JOIN profile_series ps ON ps.series_id=s.id AND ps.profile_id=? ORDER BY s.id DESC
            ''', (profile_id,))]
            for row in series:
                row['status'] = row.pop('personal_status')
                row['favorite'] = bool(row['favorite'])
            return {
                'dashboard': dashboard(db, profile_id),
                'active_profile_id': profile_id,
                'profiles': [dict(row) for row in db.execute("SELECT p.id,p.name,p.color,p.avatar,p.description, (SELECT COUNT(*) FROM profile_series WHERE profile_id=p.id) AS series_count, (SELECT COUNT(*) FROM profile_series WHERE profile_id=p.id AND favorite=1) AS favorites_count, (SELECT COUNT(*) FROM profile_episode_reviews WHERE profile_id=p.id) AS rated_count, (SELECT COUNT(*) FROM profile_series WHERE profile_id=p.id AND status='Pendiente') AS pending_count FROM profiles p" + (" WHERE p.owner_id=?" if self.owner_id is not None else "") + " ORDER BY p.id", (self.owner_id,) if self.owner_id is not None else ())],
                'notes': db.execute('SELECT notes FROM profiles WHERE id=?', (profile_id,)).fetchone()['notes'],
                'series': series,
                'reviews': [dict(row) for row in db.execute('SELECT r.*,e.series_id,e.title AS episode_title,e.season,e.number FROM profile_episode_reviews r JOIN episodes e ON e.id=r.episode_id WHERE r.profile_id=?', (profile_id,))],
                'settings': self.read_settings(db),
            }

    def read_settings(self, db):
        row = db.execute('SELECT settings FROM accounts WHERE id=?', (self.owner_id,)).fetchone() if self.owner_id is not None else None
        return json.loads(row['settings'] if row and row['settings'] else db.execute('SELECT value FROM settings WHERE id=1').fetchone()['value'])

    def profile(self, body):
        with self.database.connect() as db:
            if self.owner_id is not None:
                return db.execute('INSERT INTO profiles(name,color,avatar,description,owner_id) VALUES(?,?,?,?,?)', (body.name,body.color,body.avatar,body.description,self.owner_id)).lastrowid
            return db.execute('INSERT INTO profiles(name,color,avatar,description) VALUES(?,?,?,?)', (body.name, body.color, body.avatar, body.description)).lastrowid

    def edit_profile(self, profile_id, body):
        with self.database.connect() as db:
            db.execute('UPDATE profiles SET name=?,color=? WHERE id=?', (body.name, body.color, profile_id))
            if 'description' in body.model_fields_set:
                db.execute('UPDATE profiles SET description=? WHERE id=?', (body.description, profile_id))
            if 'avatar' in body.model_fields_set:
                db.execute('UPDATE profiles SET avatar=? WHERE id=?', (body.avatar, profile_id))

    def series(self, body, profile_id):
        fields = ('catalog_source', 'title', 'genre', 'year', 'status', 'description', 'color', 'catalog_id', 'image_url', 'source_url', 'original_title')
        with self.database.connect() as db:
            existing = db.execute('SELECT id FROM series WHERE catalog_source=? AND catalog_id=?', (body.catalog_source, body.catalog_id)).fetchone() if body.catalog_id else None
            if existing:
                series_id = existing['id']
                if db.execute('SELECT 1 FROM profile_series WHERE profile_id=? AND series_id=?', (profile_id, series_id)).fetchone():
                    raise HTTPException(409, 'Esta serie ya está en tu biblioteca')
            else:
                series_id = db.execute(f"INSERT INTO series({','.join(fields)}) VALUES({','.join('?' for _ in fields)})", tuple(getattr(body, field) for field in fields)).lastrowid
            db.execute('INSERT INTO profile_series(profile_id,series_id,status,favorite) VALUES(?,?,?,?)', (profile_id, series_id, body.status, int(body.favorite)))
            record_activity(db, profile_id, series_id, 'added')

    def status(self, body, profile_id):
        with self.database.connect() as db:
            if not db.execute('SELECT series_id FROM profile_series WHERE series_id=? AND profile_id=?', (body.id, profile_id)).fetchone(): raise HTTPException(404, 'La serie no existe')
            db.execute('INSERT INTO profile_series(profile_id,series_id,status) VALUES(?,?,?) ON CONFLICT(profile_id,series_id) DO UPDATE SET status=excluded.status', (profile_id, body.id, body.status))
            record_activity(db, profile_id, body.id, 'status', body.status)

    def favorite(self, body, profile_id):
        with self.database.connect() as db:
            if not db.execute('SELECT series_id FROM profile_series WHERE series_id=? AND profile_id=?', (body.id, profile_id)).fetchone(): raise HTTPException(404, 'La serie no existe')
            db.execute('INSERT INTO profile_series(profile_id,series_id,favorite) VALUES(?,?,?) ON CONFLICT(profile_id,series_id) DO UPDATE SET favorite=excluded.favorite', (profile_id, body.id, int(body.favorite)))

    def notes(self, body, profile_id):
        with self.database.connect() as db:
            db.execute('UPDATE profiles SET notes=? WHERE id=?', (body.notes, profile_id))

    def settings(self, body):
        with self.database.connect() as db:
            if self.owner_id is not None:
                db.execute('UPDATE accounts SET settings=? WHERE id=?',(body.model_dump_json(),self.owner_id))
            else:
                db.execute('UPDATE settings SET value=? WHERE id=1', (body.model_dump_json(),))

    def delete_profile(self, target_id, active_id):
        self.resolve_profile(target_id)
        with self.database.connect() as db:
            if not db.execute('SELECT id FROM profiles WHERE id=?', (target_id,)).fetchone():
                raise HTTPException(404, 'El perfil no existe')
            count = db.execute('SELECT COUNT(*) FROM profiles WHERE owner_id=?',(self.owner_id,)).fetchone()[0] if self.owner_id is not None else db.execute('SELECT COUNT(*) FROM profiles').fetchone()[0]
            if count <= 1:
                raise HTTPException(409, 'Debes conservar al menos un perfil. Crea otro antes de eliminar este.')
            db.execute('DELETE FROM profile_episode_reviews WHERE profile_id=?', (target_id,))
            db.execute('DELETE FROM profile_series WHERE profile_id=?', (target_id,))
            db.execute('DELETE FROM reviews WHERE profile_id=?', (target_id,))
            db.execute('DELETE FROM profiles WHERE id=?', (target_id,))
            remaining = db.execute('SELECT id FROM profiles WHERE owner_id=? ORDER BY id LIMIT 1',(self.owner_id,)).fetchone() if self.owner_id is not None else db.execute('SELECT id FROM profiles ORDER BY id LIMIT 1').fetchone()
            return remaining['id'] if target_id == active_id else active_id
