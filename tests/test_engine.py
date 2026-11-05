import json
import tempfile
import unittest
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from agm.engine import Engine, render_status, normalize_message


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

    def test_duplicate_delivery_after_restart_does_not_generate_twice(self):
        engine = Engine(self.db, self.provider)
        first = engine.turn("alice", "one", "World", "message-1")
        restarted = Engine(self.db, self.provider)
        replay = restarted.turn("alice", "one", "World", "message-1")
        self.assertEqual(replay, first)
        self.assertEqual(len(self.contexts), 1)
        self.assertEqual(restarted.get("alice", "one")["turn"], 1)
        with self.assertRaises(ValueError):
            restarted.turn("alice", "one", "Different content", "message-1")
        second = restarted.turn("alice", "one", "Continue", "message-2")
        self.assertEqual(second["turn"], 2)

    def test_failed_message_can_be_retried(self):
        engine = Engine(self.db, lambda messages: "invalid json")
        with self.assertRaises(ValueError):
            engine.turn("alice", "one", "World", "retry-1")
        engine.provider = self.provider
        state = engine.turn("alice", "one", "World", "retry-1")
        self.assertEqual(state["turn"], 1)

    def test_status_does_not_advance_or_invoke_model(self):
        engine = Engine(self.db, self.provider)
        before = engine.turn("alice", "one", "World")
        text = render_status(engine.get("alice", "one"))
        self.assertIn("Magic costs memories", text)
        self.assertIn("Find the missing bell", text)
        self.assertEqual(len(self.contexts), 1)
        self.assertEqual(engine.get("alice", "one"), before)

    def test_asi_mentions_preserve_command_and_story_content(self):
        address = "agent1example"
        self.assertEqual(normalize_message("@agent1example /status", address), "/status")
        self.assertEqual(normalize_message("@agent1example\n/export", address), "/export")
        self.assertEqual(normalize_message(" /help ", address), "/help")
        self.assertEqual(normalize_message("@agent1other /status", address), "@agent1other /status")
        self.assertEqual(normalize_message("@agent1examplex /status", address), "@agent1examplex /status")
        self.assertEqual(normalize_message("Mention @agent1example in the story", address), "Mention @agent1example in the story")

    def test_asi_visible_handle_mentions_are_normalized_at_the_start_only(self):
        address = 'agent1example'
        for prefix in ('@agenticgamemaster ', '@AgenticGameMaster\n',
                       '@agenticgamemaster\u00a0', '@agenticgamemaster @agenticgamemaster ',
                       '@agent1example @agenticgamemaster '):
            for command in ('/help', '/status', '/gm-status', '/review Rules: one memory. Draft: none lost.'):
                self.assertEqual(normalize_message(prefix + command, address), command)
        for untouched in ('@agenticgamemaster-other /status', '@anotheragent /review',
                          'An NPC mentions @agenticgamemaster /status in a letter.'):
            self.assertEqual(normalize_message(untouched, address), untouched)

    def test_independent_campaigns_generate_in_parallel(self):
        barrier = threading.Barrier(2)
        def parallel_provider(messages):
            barrier.wait(timeout=5)
            return self.provider(messages)
        engine = Engine(self.db, parallel_provider)
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(engine.turn, owner, "one", "World", "first")
                       for owner in ("alice", "bob")]
            states = [f.result(timeout=10) for f in futures]
        self.assertEqual([s["turn"] for s in states], [1, 1])

    def test_simultaneous_duplicate_is_generated_once_across_engines(self):
        entered = threading.Event()
        release = threading.Event()
        calls = []
        def slow_provider(messages):
            calls.append(1)
            entered.set()
            if not release.wait(timeout=5):
                raise TimeoutError("test synchronization failed")
            return self.provider(messages)
        engine = Engine(self.db, slow_provider)
        other = Engine(self.db, slow_provider)
        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(engine.turn, "alice", "one", "World", "same")
            self.assertTrue(entered.wait(timeout=5))
            duplicate = pool.submit(other.turn, "alice", "one", "World", "same")
            release.set()
            self.assertEqual(first.result(timeout=10), duplicate.result(timeout=10))
        self.assertEqual(len(calls), 1)
        self.assertEqual(engine.get("alice", "one")["turn"], 1)


if __name__ == "__main__":
    unittest.main()
