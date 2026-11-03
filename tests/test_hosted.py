import copy
import json
import runpy
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from datetime import datetime, timezone
from uuid import uuid4
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


class HostedAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_status_uses_hosted_single_argument_logger_and_sends_reply(self):
        class HostedLogger:
            def info(self, message):
                self.message = message
            def error(self, message):
                raise AssertionError(message)
        class ProtocolStub:
            def __init__(self, **kwargs):
                pass
            def on_message(self, model):
                return lambda handler: handler
        agent = SimpleNamespace(address='agent1example', include=lambda *args, **kwargs: None)
        with patch('uagents.Agent', return_value=agent), patch('uagents.Protocol', ProtocolStub):
            hosted = runpy.run_path(str(ROOT/'hosted/agent.py'))
        store = Storage()
        messages = []
        async def send(sender, message):
            messages.append(message)
        ctx = SimpleNamespace(storage=store, session='one', logger=HostedLogger(), send=send)
        msg = hosted['ChatMessage'](timestamp=datetime.now(timezone.utc), msg_id=uuid4(),
                                   content=[hosted['TextContent'](type='text', text='@agent1example /status')])
        await hosted['handle_message'](ctx, 'alice', msg)
        self.assertEqual(len(messages), 2)
        self.assertIn('No campaign', messages[1].content[0].text)
        self.assertIn('turn=0', ctx.logger.message)

