import copy
import json
import runpy
import tempfile
import unittest
from pathlib import Path
from agm.engine import Engine

ROOT = Path(__file__).resolve().parents[1]
HOSTED = runpy.run_path(str(ROOT / 'hosted/agent.py'), init_globals={'_AGM_TEST_MODE': True})


class Storage:
    def __init__(self):
        self.values = {}
    def get(self, key):
        return copy.deepcopy(self.values.get(key))
    def set(self, key, value):
        self.values[key] = copy.deepcopy(value)


class HostedTests(unittest.TestCase):
    def provider(self, messages):
        return json.dumps({'adventure': 'Playable scene', 'canon': ['Magic costs memories'],
                           'open_threads': ['Help the keeper?'], 'changes': []})

    def test_portable_story_logic_matches_local_engine(self):
        with tempfile.TemporaryDirectory() as directory:
            engine = Engine(Path(directory)/'state.db', self.provider)
            local = engine.turn('a', 's', 'A world')
            hosted = HOSTED['advance_state'](None, 'A world', self.provider)
            self.assertEqual(local, hosted)
            self.assertEqual(engine.turn('a', 's', 'Continue'),
                             HOSTED['advance_state'](hosted, 'Continue', self.provider))

    def test_storage_survives_invocation_and_duplicate_without_new_model_call(self):
        store = Storage()
        process = HOSTED['process_request']
        first = process(store, 'alice', 'one', 'm1', 'World', 'agent1example', self.provider)
        def forbidden(messages):
            raise AssertionError('Must not generate')
        restarted = runpy.run_path(str(ROOT/'hosted/agent.py'), init_globals={'_AGM_TEST_MODE': True})
        again = restarted['process_request'](store, 'alice', 'one', 'm1', 'World', 'agent1example', forbidden)
        self.assertEqual(first, again)
        before = copy.deepcopy(store.values)
        status = process(store, 'alice', 'one', 'm2', '@agent1example /status', 'agent1example', forbidden)
        self.assertIn('turn 1', status)
        self.assertEqual(before, store.values)
        self.assertIn('No campaign', process(store, 'bob', 'one', 'm3', '/status', 'agent1example', forbidden))

    def test_invalid_model_result_does_not_overwrite_storage(self):
        store = Storage()
        process = HOSTED['process_request']
        process(store, 'alice', 'one', 'm1', 'World', 'agent1example', self.provider)
        before = copy.deepcopy(store.values)
        with self.assertRaises(ValueError):
            process(store, 'alice', 'one', 'm2', 'Continue', 'agent1example', lambda messages:'broken')
        self.assertEqual(before, store.values)

    def test_spoiler_safe_status_hides_untagged_secrets_and_hooks(self):
        store = Storage()
        process = HOSTED['process_request']
        def secret_provider(messages):
            return json.dumps({'adventure': 'A scene',
                'canon': ['Maren secretly answered the drowned daughter'],
                'open_threads': ['The Deep Chorus is the missing memories'], 'changes': []})
        process(store, 'alice', 'one', 'm1', 'World', 'agent1example', secret_provider)
        before = copy.deepcopy(store.values)
        def forbidden(messages):
            raise AssertionError('Status must not call the model')
        safe = process(store, 'alice', 'one', 'm2', '/status', 'agent1example', forbidden)
        self.assertNotIn('Maren', safe)
        self.assertNotIn('Deep Chorus', safe)
        full = process(store, 'alice', 'one', 'm3', '/gm-status', 'agent1example', forbidden)
        self.assertIn('Maren', full)
        self.assertIn('Deep Chorus', full)
        self.assertEqual(before, store.values)
