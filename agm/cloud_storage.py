"""Durable Object-backed campaign storage. Local SQLite is scratch space only."""
import hashlib
import json
import os
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from .engine import Engine, session_lock


class CloudStore:
    def __init__(self, url, token):
        if not url.startswith("https://") or not token:
            raise ValueError("Cloud storage requires an HTTPS URL and a storage token.")
        self.url = url.rstrip("/") + "/internal/storage"
        self.token = token

    def call(self, owner, session, operation, **fields):
        payload = json.dumps(dict(owner=owner, session=session, operation=operation, **fields)).encode()
        request = urllib.request.Request(self.url, data=payload, headers={
            "Authorization": "Bearer " + self.token, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code == 409:
                raise ValueError("Campaign changed elsewhere; retry with the current state.") from None
            raise RuntimeError(f"Durable storage request failed (HTTP {exc.code}).") from None


class CloudEngine:
    def __init__(self, store=None, provider=None):
        self.store = store or CloudStore(os.environ["AGM_STORAGE_URL"], os.environ["AGM_STORAGE_TOKEN"])
        self.provider = provider

    def get(self, owner, session):
        return self.store.call(owner, session, "read")["state"]

    def turn(self, owner, session, request, message_id=None):
        if not request.strip() or len(request) > 16000:
            raise ValueError("Send between 1 and 16000 characters.")
        fingerprint = hashlib.sha256(request.encode()).hexdigest()
        with session_lock("cloud-campaigns", owner, session):
            snapshot = self.store.call(owner, session, "read", message_id=message_id)
            cached = snapshot.get("reply")
            if cached:
                if cached["fingerprint"] != fingerprint:
                    raise ValueError("Message ID reused with different content.")
                return cached["state"]
            # Reuse the tested campaign engine; discard scratch DB after remote commit.
            with tempfile.TemporaryDirectory() as directory:
                engine = Engine(Path(directory) / "scratch.db", self.provider)
                if snapshot["state"] is not None:
                    with engine.connect() as conn:
                        conn.execute("INSERT INTO sessions VALUES (?,?,?)",
                                     (owner, session, json.dumps(snapshot["state"])))
                result = engine.turn(owner, session, request)
                committed = self.store.call(owner, session, "commit", revision=snapshot["revision"],
                                            state=result, message_id=message_id, fingerprint=fingerprint)
                return committed["state"]
