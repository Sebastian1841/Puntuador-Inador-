import html
import json
import re
import time
import logging
import httpx
from fastapi import HTTPException
from .anime_catalog import search_anime
from .catalog_titles import normalize, resolve_title, LOCAL_TITLES

GENRES = {'Animation': 'Animación', 'Adventure': 'Aventura', 'Fantasy': 'Fantasía', 'Comedy': 'Comedia', 'Horror': 'Terror', 'Science-Fiction': 'Ciencia ficción', 'Crime': 'Crimen', 'Mystery': 'Misterio', 'Action': 'Acción'}


def map_show(show):
    return {
        'catalog_source': 'tvmaze',
        'catalog_id': show['id'],
        'title': LOCAL_TITLES.get(show['id'], show['name']),
        'original_title': show['name'],
        'year': int(show['premiered'][:4]) if show.get('premiered') else None,
        'genre': ', '.join(GENRES.get(g, g) for g in show.get('genres', []))[:40] or 'Sin género',
        'description': html.unescape(re.sub('<[^>]*>', '', show.get('summary') or ''))[:2000],
        'image_url': (show.get('image') or {}).get('medium', ''),
        'source_url': show['url'],
    }


class Catalog:
    def __init__(self, database, client):
        self.database = database
        self.client = client

    def search(self, query, source='tvmaze'):
        if source not in ('tvmaze', 'jikan'):
            raise HTTPException(400, 'Catálogo desconocido')
        query = query.strip()
        if not 2 <= len(query) <= 100:
            raise HTTPException(400, 'Escribe entre 2 y 100 caracteres para buscar')
        term = resolve_title(query)
        key = 'titles-v3:' + source + ':' + normalize(term)
        with self.database.connect() as db:
            cached = db.execute('SELECT results,updated FROM catalog_cache WHERE query=?', (key,)).fetchone()
        if cached and cached['updated'] > time.time() - 3600:
            return json.loads(cached['results']), False
        try:
            if source == 'jikan':
                results = search_anime(self.client, term)
            else:
                response = self.client.get('https://api.tvmaze.com/search/shows', params={'q': term})
                response.raise_for_status()
                results = [map_show(entry['show']) for entry in response.json()]
        except (httpx.HTTPError, ValueError, KeyError, TypeError) as error:
            logging.getLogger(__name__).warning('Catalog %s failed: %s: %s', source, type(error).__name__, error)
            if cached:
                return json.loads(cached['results']), True
            if isinstance(error, httpx.HTTPStatusError) and error.response.status_code == 429:
                raise HTTPException(503, 'El catálogo está ocupado. Espera unos segundos y reintenta.') from error
            raise HTTPException(502, 'No se pudo conectar con el catálogo seleccionado. Revisa tu conexión y vuelve a buscar; también puedes agregar la serie manualmente.') from error
        with self.database.connect() as db:
            db.execute('INSERT INTO catalog_cache VALUES(?,?,?) ON CONFLICT(query) DO UPDATE SET results=excluded.results,updated=excluded.updated', (key, json.dumps(results), time.time()))
            db.execute('DELETE FROM catalog_cache WHERE query NOT IN (SELECT query FROM catalog_cache ORDER BY updated DESC LIMIT 200)')
        return results, False
