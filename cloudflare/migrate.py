"""Copy existing campaigns to an empty cloud store; never overwrite cloud turns."""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dotenv import load_dotenv
from agm.cloud_storage import CloudStore
import os

parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True, help='HTTPS Worker URL')
parser.add_argument('--db', default='data/campaigns.db')
parser.add_argument('--apply', action='store_true', help='Copy and verify; default is local preview only')
args = parser.parse_args()
load_dotenv('.env')
if not Path(args.db).is_file():
    raise SystemExit('Source database not found; nothing sent.')
with sqlite3.connect(f'file:{Path(args.db).resolve().as_posix()}?mode=ro', uri=True) as conn:
    rows = conn.execute('SELECT owner,id,state FROM sessions').fetchall()
print(f'Campaigns available for migration: {len(rows)}')
if not args.apply:
    print('Preview only. No data sent. Add --apply after verifying the destination.')
    raise SystemExit(0)
store = CloudStore(args.url, os.environ.get('AGM_STORAGE_TOKEN', ''))
for index, (owner, session, raw) in enumerate(rows, 1):
    state = json.loads(raw)
    store.call(owner, session, 'import', state=state)
    if store.call(owner, session, 'read')['state'] != state:
        raise SystemExit('Verification failed; migration stopped. Keep local backup.')
    print(f'Campaign {index}: copied and verified at turn {state["turn"]}')
print('Migration complete. Source database was not modified. Prior response cache is not migrated.')
