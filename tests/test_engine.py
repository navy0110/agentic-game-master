import json
import tempfile
import unittest
from pathlib import Path
from agm.engine import Engine


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "state.db"
        self.contexts = []

    def tearDown(self):
        self.tmp.cleanup()

    def provider(self, messages):
        self.contexts.append(json.loads(messages[1]["content"]))
        return json.dumps({"adventure": "A playable scene", "canon": ["Magic costs memories"],
                           "open_threads": ["Find the missing bell"], "changes": ["The gate opened"]})

    def test_continuity_survives_restart_and_owners_are_isolated(self):
        first = Engine(self.db, self.provider)
        first.turn("alice", "one", "World: magic costs memories. A short quest.")
        second = Engine(self.db, self.provider)
        result = second.turn("alice", "one", "Players open the gate.")
        self.assertEqual(result["turn"], 2)
        self.assertEqual(self.contexts[1]["previous_state"]["turn"], 1)
        self.assertIn("magic costs memories", self.contexts[1]["world"])
        self.assertIsNone(second.get("bob", "one"))
        self.assertIsNone(second.get("alice", "other"))

    def test_bad_model_output_does_not_destroy_campaign(self):
        engine = Engine(self.db, self.provider)
        before = engine.turn("alice", "one", "A world without dragons")
        engine.provider = lambda messages: '{"adventure": "broken"}'
        with self.assertRaises(ValueError):
            engine.turn("alice", "one", "Continue")
        self.assertEqual(engine.get("alice", "one"), before)

    def test_provider_failure_leaves_no_partial_session(self):
        def failing(messages):
            raise TimeoutError("unavailable")
        engine = Engine(self.db, failing)
        with self.assertRaises(TimeoutError):
            engine.turn("alice", "one", "A new world")
        self.assertIsNone(engine.get("alice", "one"))

    def test_prior_canon_not_silently_dropped(self):
        engine = Engine(self.db, self.provider)
        engine.turn("alice", "one", "Magic costs memories")
        engine.provider = lambda messages: json.dumps({"adventure": "Next scene", "canon": [],
                                                       "open_threads": [], "changes": []})
        self.assertIn("Magic costs memories", engine.turn("alice", "one", "Continue")["canon"])


if __name__ == "__main__":
    unittest.main()
