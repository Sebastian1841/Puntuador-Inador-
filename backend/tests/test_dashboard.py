import tempfile
import unittest
from pathlib import Path
from fastapi.testclient import TestClient
from app.main import create_app
from app.database import Database

class DashboardTests(unittest.TestCase):
    def test_activity_and_schedule_are_personal_and_persistent(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'dashboard.sqlite'
            with TestClient(create_app(path)) as client:
                series=client.post('/api/series',json={'title':'Mi serie','genre':'Drama','year':2026,'status':'Viendo'}).json()['series'][0]
                sid=series['id']
                eid=client.post(f'/api/series/{sid}/episodes',json={'season':1,'number':1,'title':'Siguiente'}).json()[0]['id']
                with Database(path).connect() as db:
                    db.execute("UPDATE episodes SET airdate=date('now','+1 day') WHERE id=?",(eid,))
                state=client.post('/api/episode-reviews',json={'episode_id':eid,'score':4.5}).json()
                self.assertEqual([a['kind'] for a in state['dashboard']['activity']],['rated','added'])
                self.assertEqual(state['dashboard']['activity'][0]['detail'],'4.5')
                self.assertEqual(state['dashboard']['upcoming'][0]['id'],eid)
                other=client.post('/api/profiles',json={'name':'Otra persona'}).json()
                self.assertEqual(other['dashboard'],{'activity':[],'upcoming':[]})
                done=client.post('/api/status',json={'id':sid,'status':'Terminada'}).json()
                self.assertEqual(done['dashboard']['upcoming'],[])
                self.assertEqual(done['dashboard']['activity'][0]['kind'],'status')
            with TestClient(create_app(path)) as client:
                self.assertEqual(len(client.get('/api/state').json()['dashboard']['activity']),3)
