import tempfile
import unittest
from pathlib import Path
import httpx
from fastapi.testclient import TestClient
from app.main import create_app

class AnimeTests(unittest.TestCase):
    def test_search_save_paginate_refresh_and_isolate(self):
        offline = False
        def provider(request):
            if offline:
                return httpx.Response(429)
            if request.url.path == '/v4/anime':
                self.assertEqual(request.url.params['q'], 'The Apothecary Diaries')
                return httpx.Response(200,json={'data':[{'mal_id':54492,'title':'Kusuriya no Hitorigoto','title_english':'The Apothecary Diaries','year':2023,'genres':[{'name':'Mystery'}],'images':{'jpg':{'image_url':'https://cdn.myanimelist.net/images/anime/1708/138033.jpg'}},'url':'https://myanimelist.net/anime/54492/Kusuriya_no_Hitorigoto'}]})
            page = int(request.url.params['page'])
            return httpx.Response(200,json={'data':[{'mal_id':page,'title':f'Episode {page}','aired':'2023-10-22T00:00:00+00:00'}],'pagination':{'has_next_page':page==1}})
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'anime.sqlite'
            with TestClient(create_app(path,httpx.MockTransport(provider))) as client:
                response=client.get('/api/catalog/search',params={'q':'los diarios de la boticaria','source':'jikan'})
                self.assertEqual(response.status_code,200,response.text)
                show=response.json()[0]
                self.assertEqual(show['catalog_source'],'jikan')
                added=client.post('/api/series',json={**show,'status':'Viendo'})
                self.assertEqual(added.status_code,200,added.text)
                sid=added.json()['series'][0]['id']
                # Same numeric ID in another provider is a different catalog entry.
                other=client.post('/api/series',json={'title':'Different show','genre':'Drama','year':2023,'status':'Pendiente','catalog_id':54492})
                self.assertEqual(other.status_code,200)
                self.assertEqual(len(other.json()['series']),2)
                sync=f'/api/series/{sid}/episodes/sync'
                episodes=client.post(sync).json()
                self.assertEqual([e['number'] for e in episodes],[1,2])
                eid=episodes[0]['id']
                client.post('/api/episode-reviews',json={'episode_id':eid,'score':4.5})
                refreshed=client.post(sync).json()
                self.assertEqual(refreshed[0]['id'],eid)
                self.assertEqual(refreshed[0]['score'],4.5)
                offline=True
                self.assertEqual(client.post(sync).status_code,502)
                self.assertEqual(client.get(f'/api/series/{sid}/episodes').json()[0]['score'],4.5)
                second=client.post('/api/profiles',json={'name':'Otro'}).json()['active_profile_id']
                self.assertEqual(client.get(f'/api/series/{sid}/episodes',headers={'X-Profile-Id':str(second)}).status_code,404)
                self.assertEqual(client.get('/api/catalog/search',params={'q':'unknown','source':'jikan'}).status_code,503)
            with TestClient(create_app(path)) as client:
                self.assertEqual(len(client.get('/api/state').json()['series']),2)
