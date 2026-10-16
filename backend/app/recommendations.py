import json
from collections import Counter


def recommend(database, series):
    owned = {(s.get('catalog_source') or 'tvmaze', s.get('catalog_id')) for s in series}
    titles = {s['title'].casefold() for s in series}
    genres = Counter()
    for item in series:
        weight = 3 if item.get('favorite') else 2 if item['status'] == 'Viendo' else 1
        for genre in item['genre'].split(','):
            genres[genre.strip().casefold()] += weight
    candidates = {}
    with database.connect() as db:
        rows = db.execute('SELECT results FROM catalog_cache ORDER BY updated DESC').fetchall()
    for row in rows:
        for item in json.loads(row['results']):
            identity = (item.get('catalog_source') or 'tvmaze', item.get('catalog_id'))
            if identity in owned or item['title'].casefold() in titles or not item.get('image_url'):
                continue
            candidates.setdefault(identity, item)
    def affinity(item):
        return sum(genres[g.strip().casefold()] for g in item.get('genre', '').split(','))
    ranked = sorted(candidates.values(), key=affinity, reverse=True)[:60]
    for item in ranked:
        matches = [g.strip() for g in item.get('genre', '').split(',') if genres[g.strip().casefold()]]
        item['recommendation_reason'] = ('Coincide con tus gustos: ' + ', '.join(matches)) if matches else 'Para descubrir otros géneros'
    return ranked
