"""Add personal progress without replacing the former single-profile records."""


def migrate_profiles(db):
    if 'description' not in {r['name'] for r in db.execute('PRAGMA table_info(profiles)')}:
        db.execute("ALTER TABLE profiles ADD COLUMN description TEXT NOT NULL DEFAULT ''")
    if 'avatar' not in {r['name'] for r in db.execute('PRAGMA table_info(profiles)')}:
        db.execute("ALTER TABLE profiles ADD COLUMN avatar TEXT NOT NULL DEFAULT ''")
    if not db.execute('SELECT id FROM profiles LIMIT 1').fetchone():
        db.execute("INSERT INTO profiles(name,color) VALUES('Mi perfil','#FF6600')")
    if 'notes' not in {r['name'] for r in db.execute('PRAGMA table_info(profiles)')}:
        db.execute("ALTER TABLE profiles ADD COLUMN notes TEXT NOT NULL DEFAULT ''")
    db.executescript('''
        CREATE TABLE IF NOT EXISTS profile_episode_reviews(
          profile_id INTEGER NOT NULL REFERENCES profiles(id),
          episode_id INTEGER NOT NULL REFERENCES episodes(id) ON DELETE CASCADE,
          score REAL NOT NULL CHECK(score>=0.5 AND score<=5 AND score*2=CAST(score*2 AS INTEGER)),
          comment TEXT NOT NULL DEFAULT '', PRIMARY KEY(profile_id,episode_id));
        CREATE TABLE IF NOT EXISTS profile_series(
          profile_id INTEGER NOT NULL REFERENCES profiles(id),
          series_id INTEGER NOT NULL REFERENCES series(id) ON DELETE CASCADE,
          status TEXT NOT NULL DEFAULT 'Pendiente', favorite INTEGER NOT NULL DEFAULT 0,
          PRIMARY KEY(profile_id,series_id));
        CREATE TABLE IF NOT EXISTS migrations(name TEXT PRIMARY KEY);
    ''')
    if not db.execute("SELECT name FROM migrations WHERE name='personal-profiles-v1'").fetchone():
        profile = db.execute('SELECT id FROM profiles ORDER BY id LIMIT 1').fetchone()['id']
        db.execute('INSERT OR IGNORE INTO profile_episode_reviews SELECT ?,episode_id,score,comment FROM episode_reviews', (profile,))
        db.execute('INSERT OR IGNORE INTO profile_series(profile_id,series_id,status) SELECT ?,id,status FROM series', (profile,))
        db.execute("INSERT INTO migrations VALUES('personal-profiles-v1')")

    # Preserve ownership implied by ratings created before libraries became individual.
    if not db.execute("SELECT name FROM migrations WHERE name='individual-libraries-v1'").fetchone():
        db.execute("INSERT OR IGNORE INTO profile_series(profile_id,series_id,status) SELECT DISTINCT r.profile_id,e.series_id,'Viendo' FROM profile_episode_reviews r JOIN episodes e ON e.id=r.episode_id")
        db.execute("INSERT INTO migrations VALUES('individual-libraries-v1')")

    db.execute("""CREATE TABLE IF NOT EXISTS profile_activity(
        id INTEGER PRIMARY KEY, profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
        series_id INTEGER NOT NULL REFERENCES series(id) ON DELETE CASCADE,
        kind TEXT NOT NULL, detail TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')))
    """)
