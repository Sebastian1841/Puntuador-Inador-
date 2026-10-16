"""SQLite online backup and explicit offline restore. Run from backend/."""
from contextlib import closing
import argparse
import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.database import default_database

parser=argparse.ArgumentParser()
parser.add_argument('action',choices=['backup','restore'])
parser.add_argument('file',type=Path)
parser.add_argument('--confirm-offline',action='store_true')
args=parser.parse_args()
active=default_database().resolve()
target=args.file.resolve()
if target==active:
    parser.error('Source and destination must differ')
if args.action=='backup':
    if target.exists(): parser.error('Destination already exists')
    source=sqlite3.connect(active.as_uri()+'?mode=ro',uri=True)
    target.parent.mkdir(parents=True,exist_ok=True)
    with closing(sqlite3.connect(target)) as out: source.backup(out)
    source.close()
    print('Backup created:',target)
else:
    if not args.confirm_offline: parser.error('Stop the API first and pass --confirm-offline')
    source=sqlite3.connect(target.as_uri()+'?mode=ro',uri=True)
    if source.execute('PRAGMA integrity_check').fetchone()[0]!='ok': parser.error('Invalid SQLite database')
    tables={r[0] for r in source.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not {'profiles','series','settings'}.issubset(tables): parser.error('Not a Puntuador database')
    active.parent.mkdir(parents=True,exist_ok=True)
    if active.exists():
        backup=active.with_name(active.name+'.before-restore-'+datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f'))
        with closing(sqlite3.connect(active)) as old, closing(sqlite3.connect(backup)) as out: old.backup(out)
        print('Previous database backed up:',backup)
    temporary=active.with_suffix('.restore-tmp')
    if temporary.exists(): parser.error('Temporary restore file already exists; inspect it before retrying')
    with closing(sqlite3.connect(temporary)) as out: source.backup(out)
    source.close()
    os.replace(temporary,active)
    print('Restored:',active)
