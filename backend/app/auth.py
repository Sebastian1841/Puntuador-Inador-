"""Invite-only accounts and opaque, revocable cookie sessions."""
import hashlib
import hmac
import os
import secrets
import sqlite3
import time
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

router = APIRouter(prefix='/api/auth')
COOKIE = 'puntuador_session'

def password_hash(password):
    salt = secrets.token_hex(16)
    digest = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1).hex()
    return salt + ':' + digest

def password_valid(password, encoded):
    salt, digest = encoded.split(':')
    actual = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1).hex()
    return hmac.compare_digest(actual, digest)

def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()

class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=60, pattern=r'^[a-zA-Z0-9_.-]+$')
    password: str = Field(min_length=12, max_length=128)

class Registration(Credentials):
    invitation: str = Field(min_length=20, max_length=200)

class Auth:
    def __init__(self, database, production=False):
        self.database = database
        self.production = production
        self.enabled = production or os.environ.get('AUTH_ENABLED') == '1'
        # A database that already contains accounts must never silently become public.
        with database.connect() as db:
            if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='accounts'").fetchone():
                self.enabled = self.enabled or bool(db.execute('SELECT 1 FROM accounts LIMIT 1').fetchone())
        if not self.enabled:
            return
        self.dummy_password = password_hash(secrets.token_urlsafe(32))
        with database.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS accounts(id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, password TEXT NOT NULL, admin INTEGER NOT NULL DEFAULT 0, settings TEXT);
            CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY, account_id INTEGER NOT NULL REFERENCES accounts(id), expires REAL NOT NULL);
            CREATE TABLE IF NOT EXISTS invitations(token TEXT PRIMARY KEY, expires REAL NOT NULL, used INTEGER NOT NULL DEFAULT 0);
            CREATE TABLE IF NOT EXISTS login_attempts(key TEXT PRIMARY KEY, count INTEGER NOT NULL, expires REAL NOT NULL);
            """)
            if 'owner_id' not in {r['name'] for r in db.execute('PRAGMA table_info(profiles)')}:
                db.execute('ALTER TABLE profiles ADD COLUMN owner_id INTEGER REFERENCES accounts(id)')
            if not db.execute('SELECT 1 FROM accounts LIMIT 1').fetchone():
                username = os.environ.get('ADMIN_USERNAME', '')
                password = os.environ.get('ADMIN_PASSWORD', '')
                if len(username) < 3 or len(password) < 12:
                    raise RuntimeError('Set ADMIN_USERNAME and ADMIN_PASSWORD (at least 12 characters) before enabling authentication.')
                Credentials(username=username,password=password)
                aid = db.execute('INSERT INTO accounts(username,password,admin) VALUES(?,?,1)', (username.lower(), password_hash(password))).lastrowid
                db.execute('UPDATE profiles SET owner_id=? WHERE owner_id IS NULL', (aid,))

    def account(self, request):
        token = request.cookies.get(COOKIE, '')
        if not token:
            return None
        with self.database.connect() as db:
            row = db.execute('SELECT a.id,a.username,a.admin FROM accounts a JOIN sessions s ON s.account_id=a.id WHERE s.token=? AND s.expires>?', (token_hash(token), time.time())).fetchone()
            return dict(row) if row else None

    def session(self, response, aid, old=''):
        token = secrets.token_urlsafe(32)
        with self.database.connect() as db:
            db.execute('DELETE FROM sessions WHERE expires<? OR token=?', (time.time(), token_hash(old)))
            db.execute('INSERT INTO sessions VALUES(?,?,?)', (token_hash(token), aid, time.time()+14*86400))
        response.set_cookie(COOKIE, token, max_age=14*86400, httponly=True, secure=self.production, samesite='lax', path='/')

    def throttle(self, key):
        with self.database.connect() as db:
            db.execute('DELETE FROM login_attempts WHERE expires<?', (time.time(),))
            row = db.execute('SELECT count FROM login_attempts WHERE key=?', (key,)).fetchone()
            if row and row['count'] >= 10:
                raise HTTPException(429, 'Demasiados intentos. Espera 15 minutos.')
            db.execute('INSERT INTO login_attempts VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET count=count+1', (key,time.time()+900))

def service(request):
    auth = request.app.state.auth
    if not auth.enabled:
        raise HTTPException(404, 'Acceso local sin cuentas')
    return auth

@router.get('/me')
def me(request: Request):
    return {'enabled': request.app.state.auth.enabled, 'account': request.app.state.auth.account(request) if request.app.state.auth.enabled else None}

@router.post('/login')
def login(body: Credentials, request: Request, response: Response):
    auth = service(request)
    auth.throttle('login:'+body.username.lower())
    with auth.database.connect() as db:
        row = db.execute('SELECT * FROM accounts WHERE username=?',(body.username.lower(),)).fetchone()
    valid = password_valid(body.password, row['password'] if row else auth.dummy_password)
    if not row or not valid:
        raise HTTPException(401,'Usuario o contraseña incorrectos')
    with auth.database.connect() as db:
        db.execute('DELETE FROM login_attempts WHERE key=?',('login:'+body.username.lower(),))
    auth.session(response,row['id'],request.cookies.get(COOKIE,''))
    return {'ok':True}

@router.post('/register')
def register(body: Registration, request: Request, response: Response):
    auth = service(request)
    auth.throttle('register:'+token_hash(body.invitation))
    hashed = password_hash(body.password)
    with auth.database.connect() as db:
        db.execute('BEGIN IMMEDIATE')
        invitation = db.execute('SELECT * FROM invitations WHERE token=? AND used=0 AND expires>?',(token_hash(body.invitation),time.time())).fetchone()
        if not invitation:
            raise HTTPException(400,'Invitación inválida o vencida')
        try:
            aid=db.execute('INSERT INTO accounts(username,password) VALUES(?,?)',(body.username.lower(),hashed)).lastrowid
        except sqlite3.IntegrityError:
            raise HTTPException(409,'Ese nombre de usuario ya existe')
        db.execute('UPDATE invitations SET used=1 WHERE token=?',(token_hash(body.invitation),))
        db.execute("INSERT INTO profiles(name,color,owner_id) VALUES(?,'#008cff',?)",(body.username,aid))
    auth.session(response,aid,request.cookies.get(COOKIE,''))
    return {'ok':True}

@router.post('/logout')
def logout(request: Request, response: Response):
    auth=service(request)
    with auth.database.connect() as db:
        db.execute('DELETE FROM sessions WHERE token=?',(token_hash(request.cookies.get(COOKIE,'')),))
    response.delete_cookie(COOKIE,path='/',secure=auth.production,httponly=True,samesite='lax')
    return {'ok':True}

@router.post('/invitations')
def invite(request: Request):
    auth=service(request)
    account=auth.account(request)
    if not account or not account['admin']:
        raise HTTPException(403,'Solo el administrador puede crear invitaciones')
    token=secrets.token_urlsafe(32)
    with auth.database.connect() as db:
        db.execute('DELETE FROM invitations WHERE expires<? OR used=1',(time.time(),))
        db.execute('INSERT INTO invitations VALUES(?,?,0)',(token_hash(token),time.time()+7*86400))
    return {'invitation':token,'expires_in_days':7}

class PasswordChange(BaseModel):
    current_password: str = Field(min_length=12,max_length=128)
    new_password: str = Field(min_length=12,max_length=128)

@router.post('/password')
def change_password(body: PasswordChange, request: Request, response: Response):
    auth=service(request)
    account=auth.account(request)
    if not account:
        raise HTTPException(401,'Inicia sesión')
    auth.throttle('password:'+str(account['id']))
    with auth.database.connect() as db:
        row=db.execute('SELECT password FROM accounts WHERE id=?',(account['id'],)).fetchone()
        if not password_valid(body.current_password,row['password']):
            raise HTTPException(400,'La contraseña actual no coincide')
        db.execute('UPDATE accounts SET password=? WHERE id=?',(password_hash(body.new_password),account['id']))
        db.execute('DELETE FROM sessions WHERE account_id=?',(account['id'],))
    auth.session(response,account['id'])
    return {'ok':True}
