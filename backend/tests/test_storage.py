from contextlib import closing
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from app.database import Database

SCRIPT=Path(__file__).resolve().parents[1]/'scripts'/'storage.py'
class StorageTests(unittest.TestCase):
    def test_backup_restore_and_refusal_to_overwrite_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            active=root/'active.sqlite'
            backup=root/'backup.sqlite'
            Database(active).initialize()
            env={**os.environ,'CLUB_DB':str(active)}
            def run(*args):
                return subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],env=env,capture_output=True,text=True)
            self.assertEqual(run('backup',backup).returncode,0)
            self.assertNotEqual(run('backup',backup).returncode,0)
            with closing(sqlite3.connect(active)) as db:
                db.execute("UPDATE profiles SET name='Changed'")
                db.commit()
            self.assertNotEqual(run('restore',backup).returncode,0)
            restored=run('restore',backup,'--confirm-offline')
            self.assertEqual(restored.returncode,0,restored.stderr)
            with closing(sqlite3.connect(active)) as db:
                self.assertNotEqual(db.execute('SELECT name FROM profiles LIMIT 1').fetchone()[0],'Changed')
            self.assertTrue(list(root.glob('active.sqlite.before-restore-*')))
