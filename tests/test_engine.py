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

    def test_explicit_correction_replaces_fact_and_survives_restart(self):
        engine = Engine(self.db, self.provider)
        engine.turn("alice", "one", "World")
        def corrected(messages):
            self.contexts.append(json.loads(messages[1]["content"]))
            return json.dumps({"adventure": "The GM corrected the record.",
                "canon": ["Magic costs memories"], "open_threads": [], "changes": [],
                "corrections": [{"old": "Magic costs memories", "new": "Magic costs time",
                                 "evidence": "Correction: magic costs time."}]})
        engine.provider = corrected
        state = engine.turn("alice", "one", "Correction: magic costs time.")
        self.assertNotIn("Magic costs memories", state["canon"])
        self.assertIn("Magic costs time", state["canon"])
        self.assertEqual(state["correction_history"][0]["old"], "Magic costs memories")
        restarted = Engine(self.db, self.provider)
        self.assertEqual(restarted.get("alice", "one"), state)
        later = restarted.turn("alice", "one", "Continue")
        self.assertNotIn("Magic costs memories", later["canon"])
        context = self.contexts[-1]["previous_state"]
        self.assertNotIn("correction_history", context)
        self.assertNotIn("Magic costs memories", context["canon"])

    def test_unsubstantiated_correction_rolls_back(self):
        engine = Engine(self.db, self.provider)
        before = engine.turn("alice", "one", "World")
        engine.provider = lambda messages: json.dumps({"adventure": "Next", "canon": [],
            "open_threads": [], "changes": [], "corrections": [{"old": "Magic costs memories",
            "new": "Magic is free", "evidence": "Correction: magic is free"}]})
        with self.assertRaises(ValueError):
            engine.turn("alice", "one", "Go to the harbor")
        self.assertEqual(engine.get("alice", "one"), before)


if __name__ == "__main__":
    unittest.main()
