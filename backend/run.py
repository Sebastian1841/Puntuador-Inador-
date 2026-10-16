import os
import uvicorn
from pathlib import Path

if __name__ == '__main__':
    reload = os.environ.get('AFTERCREDITS_RELOAD') == '1'
    uvicorn.run('app.main:app', host='127.0.0.1', port=int(os.environ.get('PORT', '8000')),
                reload=reload, reload_dirs=[str(Path(__file__).parent / 'app')] if reload else None)
