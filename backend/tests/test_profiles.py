import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import create_app
from app.database import Database

class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'profiles.sqlite'
        self.client = TestClient(create_app(self.path))
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temp.cleanup()

    def test_profiles_isolate_scores_status_favorites_notes(self):
        initial = self.client.get('/api/state').json()
        first = initial['active_profile_id']
        series = self.client.post('/api/series', json={'title':'Nuestra serie','genre':'Drama','year':2026,'status':'Viendo','catalog_id':35073}).json()['series'][0]
        sid = series['id']
        eid = self.client.post(f'/api/series/{sid}/episodes',json={'season':1,'number':1,'title':'Inicio'}).json()[0]['id']
        self.client.post('/api/episode-reviews',json={'episode_id':eid,'score':4.5,'comment':'Primera opinión'})
        self.client.post('/api/favorites',json={'id':sid,'favorite':True})
        self.client.post('/api/notes',json={'notes':'Notas del primer perfil'})
        created = self.client.post('/api/profiles',json={'name':'Amiga','color':'#123456'})
        self.assertEqual(created.status_code,200)
        second = created.json()['active_profile_id']
        self.assertNotEqual(first,second)
        headers = {'X-Profile-Id':str(second)}
        state = self.client.get('/api/state',headers=headers).json()
        self.assertEqual(state['reviews'],[])
        self.assertEqual(state['notes'],'')
        self.assertEqual(state['series'], [])
        self.assertEqual(self.client.get(f'/api/series/{sid}/episodes',headers=headers).status_code,404)
        self.assertEqual(self.client.post('/api/episode-reviews',headers=headers,json={'episode_id':eid,'score':2}).status_code,404)
        added = self.client.post('/api/series',headers=headers,json={'title':'Nuestra serie','genre':'Drama','year':2026,'status':'Pendiente','catalog_id':35073})
        self.assertEqual(added.status_code,200)
        self.assertFalse(added.json()['series'][0]['favorite'])
        self.assertEqual(added.json()['series'][0]['status'],'Pendiente')
        self.assertIsNone(self.client.get(f'/api/series/{sid}/episodes',headers=headers).json()[0]['score'])
        self.client.post('/api/episode-reviews',headers=headers,json={'episode_id':eid,'score':2,'comment':'Segunda opinión'})
        self.client.post('/api/status',headers=headers,json={'id':sid,'status':'Terminada'})
        self.client.post('/api/notes',headers=headers,json={'notes':'Notas de mi amiga'})
        self.client.post('/api/profile',headers=headers,json={'name':'Nuevo nombre','color':'#abcdef'})
        first_state = self.client.get('/api/state').json()
        self.assertEqual(first_state['reviews'][0]['score'],4.5)
        self.assertEqual(first_state['reviews'][0]['comment'],'Primera opinión')
        self.assertTrue(first_state['series'][0]['favorite'])
        self.assertEqual(first_state['series'][0]['status'],'Viendo')
        self.assertEqual(first_state['notes'],'Notas del primer perfil')
        self.assertEqual(first_state['series'][0]['episode_count'],1)
        with TestClient(create_app(self.path)) as restarted:
            state = restarted.get('/api/state',headers=headers).json()
            self.assertEqual(state['reviews'][0]['score'],2)
            self.assertEqual(state['series'][0]['status'],'Terminada')
            self.assertEqual(state['notes'],'Notas de mi amiga')
            self.assertEqual(next(p for p in state['profiles'] if p['id']==second)['name'],'Nuevo nombre')
        self.assertEqual(self.client.get('/api/state',headers={'X-Profile-Id':'99999'}).status_code,404)
        self.assertEqual(self.client.get('/api/state',headers={'X-Profile-Id':'oops'}).status_code,400)

    def test_individual_libraries_and_profile_management(self):
        first = self.client.get('/api/state').json()['active_profile_id']
        sid = self.client.post('/api/series',json={'title':'Solo mia','genre':'Drama','year':2026,'status':'Viendo'}).json()['series'][0]['id']
        second = self.client.post('/api/profiles',json={'name':'Otro'}).json()['active_profile_id']
        headers = {'X-Profile-Id':str(second)}
        self.assertEqual(self.client.get('/api/state',headers=headers).json()['series'],[])
        for path, body in [('status',{'id':sid,'status':'Terminada'}),('favorites',{'id':sid,'favorite':True})]:
            self.assertEqual(self.client.post('/api/'+path,headers=headers,json=body).status_code,404)
        self.assertEqual(self.client.post(f'/api/series/{sid}/episodes',headers=headers,json={'season':1,'number':1,'title':'Ajeno'}).status_code,404)
        self.assertEqual(self.client.post(f'/api/series/{sid}/episodes/sync',headers=headers).status_code,404)
        own = self.client.post('/api/series',headers=headers,json={'title':'Solo suya','genre':'Drama','year':2026,'status':'Pendiente'}).json()['series'][0]['id']
        edited = self.client.post(f'/api/profiles/{second}',json={'name':'Editado','color':'#123456'})
        self.assertEqual(edited.status_code,200)
        self.assertEqual(edited.json()['active_profile_id'],first)
        self.assertEqual(next(p['name'] for p in edited.json()['profiles'] if p['id']==second),'Editado')
        removed = self.client.delete(f'/api/profiles/{first}')
        self.assertEqual(removed.status_code,200)
        self.assertEqual(removed.json()['active_profile_id'],second)
        self.assertEqual([s['id'] for s in removed.json()['series']],[own])
        self.assertEqual(self.client.delete(f'/api/profiles/{second}',headers=headers).status_code,409)
        self.assertEqual(self.client.post(f'/api/profiles/{first}',headers=headers,json={'name':'No existe'}).status_code,404)
        with TestClient(create_app(self.path)) as restarted:
            self.assertEqual([s['id'] for s in restarted.get('/api/state').json()['series']],[own])

    def test_single_profile_migration_runs_once(self):
        sid = self.client.post('/api/series',json={'title':'Anterior','genre':'Drama','year':2020,'status':'Viendo'}).json()['series'][0]['id']
        eid = self.client.post(f'/api/series/{sid}/episodes',json={'season':1,'number':1,'title':'Primero'}).json()[0]['id']
        with Database(self.path).connect() as db:
            db.execute("DELETE FROM migrations WHERE name='personal-profiles-v1'")
            db.execute('INSERT INTO episode_reviews VALUES(?,?,?)',(eid,3.5,'Valoración anterior'))
        with TestClient(create_app(self.path)) as migrated:
            state=migrated.get('/api/state').json()
            self.assertEqual(state['reviews'][0]['score'],3.5)
            self.assertEqual(state['reviews'][0]['comment'],'Valoración anterior')
            migrated.post('/api/episode-reviews',json={'episode_id':eid,'score':5,'comment':'Actualizada'})
        with TestClient(create_app(self.path)) as restarted:
            self.assertEqual(restarted.get('/api/state').json()['reviews'][0]['score'],5)
        with Database(self.path).connect() as db:
            self.assertEqual(db.execute('SELECT score FROM episode_reviews').fetchone()['score'],3.5)

if __name__ == '__main__': unittest.main()
