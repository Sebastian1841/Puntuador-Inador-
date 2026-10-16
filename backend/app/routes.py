from fastapi import APIRouter, Request, Response, HTTPException
from .models import ProfileInput, SeriesInput, ReviewInput, StatusInput, SettingsInput, EpisodeInput, EpisodeReviewInput, FavoriteInput, NotesInput
from .recommendations import recommend
router = APIRouter(prefix='/api')

def profile_id(request):
    return request.app.state.club.resolve_profile(request.headers.get('X-Profile-Id'))

@router.get('/health')
def health():
    return {'status': 'ok', 'backend': 'python-fastapi', 'database': 'sqlite', 'api_version': 4}

@router.get('/state')
def state(request: Request):
    return request.app.state.club.state(profile_id(request))

@router.get('/catalog/search')
def search(request: Request, response: Response, q: str = '', source: str = 'tvmaze'):
    results, stale = request.app.state.catalog.search(q, source)
    response.headers['X-Catalog-Cache'] = 'stale' if stale else 'fresh'
    return results

@router.post('/profiles')
def profile(body: ProfileInput, request: Request):
    created = request.app.state.club.profile(body)
    return request.app.state.club.state(created)

@router.post('/profile')
def edit_profile(body: ProfileInput, request: Request):
    pid = profile_id(request)
    request.app.state.club.edit_profile(pid, body)
    return request.app.state.club.state(pid)

@router.post('/series')
def series(body: SeriesInput, request: Request):
    pid = profile_id(request)
    request.app.state.club.series(body, pid)
    return request.app.state.club.state(pid)

@router.post('/reviews')
def review(body: ReviewInput, request: Request):
    raise HTTPException(410, 'Ahora se puntúan capítulos, no series completas')

@router.post('/status')
def status(body: StatusInput, request: Request):
    pid = profile_id(request)
    request.app.state.club.status(body, pid)
    return request.app.state.club.state(pid)

@router.post('/favorites')
def favorite(body: FavoriteInput, request: Request):
    pid = profile_id(request)
    request.app.state.club.favorite(body, pid)
    return request.app.state.club.state(pid)

@router.post('/notes')
def notes(body: NotesInput, request: Request):
    pid = profile_id(request)
    request.app.state.club.notes(body, pid)
    return request.app.state.club.state(pid)

@router.post('/settings')
def settings(body: SettingsInput, request: Request):
    request.app.state.club.settings(body)
    return request.app.state.club.state(profile_id(request))

@router.get('/series/{series_id}/episodes')
def episodes(series_id: int, request: Request):
    return request.app.state.episodes.list(series_id, profile_id(request))

@router.post('/series/{series_id}/episodes/sync')
def sync_episodes(series_id: int, request: Request):
    return request.app.state.episodes.sync(series_id, profile_id(request))

@router.post('/series/{series_id}/episodes')
def add_episode(series_id: int, body: EpisodeInput, request: Request):
    return request.app.state.episodes.add(series_id, body, profile_id(request))

@router.post('/episode-reviews')
def episode_review(body: EpisodeReviewInput, request: Request):
    pid = profile_id(request)
    request.app.state.episodes.rate(body, pid)
    return request.app.state.club.state(pid)


@router.post('/profiles/{target_id}')
def update_named_profile(target_id: int, body: ProfileInput, request: Request):
    active = profile_id(request)
    target = request.app.state.club.resolve_profile(target_id)
    request.app.state.club.edit_profile(target, body)
    return request.app.state.club.state(active)

@router.delete('/profiles/{target_id}')
def delete_named_profile(target_id: int, request: Request):
    active = request.app.state.club.delete_profile(target_id, profile_id(request))
    return request.app.state.club.state(active)

@router.get('/catalog/recommendations')
def recommendations(request: Request):
    state = request.app.state.club.state(profile_id(request))
    return recommend(request.app.state.catalog.database, state['series'])
