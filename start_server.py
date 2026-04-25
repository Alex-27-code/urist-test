import os, sys
_project_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_project_dir)
sys.path.insert(0, _project_dir)

from app import app
import backend.database.db_session as db_session
import backend.database.default_data as dd

db_session.global_init('data/urist.db')
dd.default_data()

port = int(os.getenv('FLASK_PORT', 5555))
host = os.getenv('FLASK_HOST', '0.0.0.0')
app.run(port=port, host=host, debug=False)
