"""MyAnimeList metadata via the public Jikan v4 API."""
import time
import threading
import httpx

_lock = threading.Lock()
_last_request = 0.0


def request(client, path, params=None):
    global _last_request
    for attempt in range(3):
        try:
            with _lock:
                delay = .4 - (time.monotonic() - _last_request)
                if delay > 0:
                    time.sleep(delay)
                _last_request = time.monotonic()
                response = client.get('https://api.jikan.moe/v4/' + path, params=params)
            response.raise_for_status()
            return response.json()
        except (httpx.TransportError, httpx.HTTPStatusError) as error:
            retryable = not isinstance(error, httpx.HTTPStatusError) or error.response.status_code in (429, 500, 502, 503, 504)
            if not retryable or attempt == 2:
                raise
            delay = 2 ** attempt
            if isinstance(error, httpx.HTTPStatusError):
                try:
                    delay = max(delay, min(10, float(error.response.headers.get('Retry-After', '0'))))
                except ValueError:
                    pass
            time.sleep(delay)


def search_anime(client, term):
    payload = request(client, 'anime', {'q': term, 'limit': 20})
    results = []
    seen = set()
    for anime in payload['data']:
        if anime['mal_id'] in seen:
            continue
        seen.add(anime['mal_id'])
        results.append({
            'catalog_source': 'jikan', 'catalog_id': anime['mal_id'],
            'title': (anime.get('title_english') or anime['title'])[:100],
            'original_title': anime['title'][:200],
            'year': anime.get('year') or (((anime.get('aired') or {}).get('prop') or {}).get('from') or {}).get('year'),
            'genre': ', '.join(g['name'] for g in anime.get('genres', []))[:40] or 'Anime',
            'description': (anime.get('synopsis') or '')[:2000],
            'image_url': ((anime.get('images') or {}).get('jpg') or {}).get('image_url') or '',
            'source_url': anime['url'],
        })
    return results


def fetch_episodes(client, anime_id):
    rows = []
    page = 1
    while True:
        payload = request(client, f'anime/{anime_id}/episodes', {'page': page})
        for episode in payload['data']:
            rows.append({'number': episode['mal_id'], 'title': episode['title'], 'airdate': (episode.get('aired') or '')[:10]})
        if not payload.get('pagination', {}).get('has_next_page'):
            return rows
        page += 1
        if page > 100:
            raise ValueError('Demasiadas páginas de capítulos')
