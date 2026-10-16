"""Profile-scoped dashboard activity and locally cached episode schedule."""
def record_activity(db, profile_id, series_id, kind, detail=''):
    db.execute('INSERT INTO profile_activity(profile_id,series_id,kind,detail) VALUES(?,?,?,?)', (profile_id,series_id,kind,detail))
    db.execute('DELETE FROM profile_activity WHERE profile_id=? AND id NOT IN (SELECT id FROM profile_activity WHERE profile_id=? ORDER BY id DESC LIMIT 100)', (profile_id,profile_id))


def dashboard(db, profile_id):
    return {
        'activity': [dict(row) for row in db.execute('SELECT a.*,s.title,s.image_url FROM profile_activity a JOIN series s ON s.id=a.series_id WHERE a.profile_id=? ORDER BY a.id DESC LIMIT 20',(profile_id,))],
        'upcoming': [dict(row) for row in db.execute("SELECT e.id,e.series_id,e.title,e.season,e.number,e.airdate,s.title AS series_title,s.image_url FROM episodes e JOIN series s ON s.id=e.series_id JOIN profile_series ps ON ps.series_id=s.id WHERE ps.profile_id=? AND ps.status!='Terminada' AND e.airdate>=date('now') ORDER BY e.airdate,e.id LIMIT 20",(profile_id,))],
    }
