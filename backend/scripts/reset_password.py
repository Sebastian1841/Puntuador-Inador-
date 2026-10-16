"""Account recovery from a trusted server terminal; never accepts passwords in arguments."""
import getpass
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.database import Database
from app.auth import password_hash
username=input('Username: ').strip().lower()
password=getpass.getpass('New password (12+ characters): ')
if not 12<=len(password)<=128 or password!=getpass.getpass('Repeat password: '):
    raise SystemExit('Invalid length or passwords do not match')
with Database().connect() as db:
    row=db.execute('SELECT id FROM accounts WHERE username=?',(username,)).fetchone()
    if not row: raise SystemExit('Account not found')
    db.execute('UPDATE accounts SET password=? WHERE id=?',(password_hash(password),row['id']))
    db.execute('DELETE FROM sessions WHERE account_id=?',(row['id'],))
print('Password updated; sessions revoked.')
