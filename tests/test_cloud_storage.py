import copy
import json
import unittest
from agm.cloud_storage import CloudEngine


class FakeStore:
    def __init__(self):
        self.snapshot = {"state": None, "revision": 0}
        self.replies = {}
        self.fail_commit = False

    def call(self, owner, session, operation, **fields):
        if operation == "read":
            return copy.deepcopy({**self.snapshot, "reply": self.replies.get(fields.get("message_id"))})
        if self.fail_commit:
            raise RuntimeError("Durable storage unavailable")
        if fields["revision"] != self.snapshot["revision"]:
            raise ValueError("Revision conflict")
        self.snapshot = {"state": fields["state"], "revision": fields["revision"] + 1}
        if fields["message_id"]:
            self.replies[fields["message_id"]] = {"state": fields["state"], "fingerprint": fields["fingerprint"]}
        return copy.deepcopy(self.snapshot)


class CloudTests(unittest.TestCase):
    def provider(self, messages):
        return json.dumps({"adventure": "A scene", "canon": ["The tower is dark"],
                           "open_threads": ["Help the keeper?"], "changes": []})

    def test_restart_recovers_campaign_and_duplicate(self):
        store = FakeStore()
        state = CloudEngine(store, self.provider).turn("a", "s", "World", "one")
        def forbidden(messages):
            raise AssertionError("Duplicate must not call the model")
        restarted = CloudEngine(store, forbidden)
        self.assertEqual(restarted.get("a", "s"), state)
        self.assertEqual(restarted.turn("a", "s", "World", "one"), state)

    def test_failed_remote_commit_does_not_claim_success_or_change_state(self):
        store = FakeStore()
        engine = CloudEngine(store, self.provider)
        before = engine.turn("a", "s", "World", "one")
        store.fail_commit = True
        with self.assertRaises(RuntimeError):
            engine.turn("a", "s", "Continue", "two")
        self.assertEqual(engine.get("a", "s"), before)
