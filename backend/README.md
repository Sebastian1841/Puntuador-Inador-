# API Python de Aftercredits

FastAPI + SQLite incluido con Python. Configuración completa en `../README.md`.

Desde `frontend`, `npm run dev` inicia toda la plataforma. Para ejecutar únicamente la API desde esta carpeta:

```powershell
.venv/Scripts/python.exe run.py
```

Puerto predeterminado: 8000. Variables opcionales: `PORT`, `CLUB_DB` (archivo SQLite). Si cambias PORT, ajusta también el proxy en `frontend/vite.config.ts`.

Dependencias: `.venv/Scripts/python.exe -m pip install -r requirements.txt`.
Pruebas: `.venv/Scripts/python.exe -m unittest discover -s tests -p "test_*.py" -v`.

No se necesitan Docker, PostgreSQL ni un servidor externo. Las llamadas al catálogo requieren internet; SQLite permanece en el equipo.
