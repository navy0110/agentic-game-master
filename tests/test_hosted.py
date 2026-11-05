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
    def test_greeting_explains_capability_without_model_or_storage(self):
        def forbidden(messages):
            raise AssertionError('Greeting must not generate')
        store = Storage()
        reply = HOSTED['process_request'](store, 'a', 's', 'm', 'hello',
                                         'agent1example', forbidden)
        self.assertIn('@agenticgamemaster', reply)
        self.assertIn('do not control a live game', reply)
        self.assertEqual(store.values, {})

    def test_command_question_needs_no_model_or_campaign(self):
        store = Storage()
        def forbidden(messages):
            raise AssertionError('Command guidance must not generate')
        reply = HOSTED['process_request'](store, 'a', 's', 'm',
            'My players can see my screen tonight. Which command gives me a spoiler-safe '
            'summary of where the campaign stands, and what extra detail does /gm-status '
            'show that I should only read alone?', 'agent1example', forbidden)
        self.assertIn('Use /status', reply)
        self.assertIn('NPC secrets', reply)
        self.assertEqual(store.values, {})

    def test_specific_requests_reach_model_without_saved_campaign(self):
        for request in (
            'I need an NPC for my harbor campaign: a port official who secretly reports '
            'to a rival trade house. Give me her motives, secret and three lines of dialogue.',
            'Continuing our campaign: the players sold the forged deed to Baron Hult '
            'instead of exposing it. Continue from that choice and list unresolved threads.'
        ):
            def provider(messages):
                context = json.loads(messages[1]['content'])
                self.assertEqual(context['request'], request)
                self.assertIsNone(context['previous_state'])
                return self.provider(messages)
            result = HOSTED['advance_state'](None, request, provider)
            self.assertEqual(result['turn'], 1)

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
    async def test_npc_fields_render_and_invalid_content_never_saves(self):
        hosted = self.load_adapter()
        prompt = ('I need an NPC for my harbor campaign: a port official. '
                  'Give me her motives, secret, and three lines of dialogue.')
        record = {'npc': {'name':'Vess Andarine', 'role':'Harbor Registrar',
                    'motives':['Protect her brother', 'Pay her debts'],
                    'secret':'Reports manifests to a rival trade house',
                    'dialogue':['The night berth is already reserved.',
                                'Some seals open doors faster.',
                                'I would not ask who paid the fee.']},
                  'canon':[], 'open_threads':[], 'changes':[], 'corrections':[]}
        def response():
            return {'choices':[{'message':{'content':json.dumps(record)}}]}
        http = SimpleNamespace(raise_for_status=lambda:None, json=response)
        with patch.dict('os.environ', {'ASI1_API_KEY':'test-only'}), \
                patch('requests.post', return_value=http) as post:
            ctx, msg, sent = self.request_context(hosted, prompt)
            await hosted['handle_message'](ctx, 'alice', msg)
            visible = sent[-1].content[0].text
            self.assertIn('Protect her brother', visible)
            self.assertIn('Reports manifests', visible)
            self.assertIn('3. "I would not ask', visible)
            self.assertEqual(post.call_args.kwargs['json']['response_format']['json_schema']['name'], 'npc_turn')
            record['npc']['dialogue'] = []
            failed_ctx, failed_msg, failed_sent = self.request_context(hosted, prompt)
            await hosted['handle_message'](failed_ctx, 'bob', failed_msg)
            self.assertEqual(failed_ctx.storage.values, {})
            self.assertIn('could not be validated', failed_sent[-1].content[0].text)
            # Regression: the exact incomplete shape previously accepted must fail.
            record.clear()
            record.update(adventure='## NPC: Vess\nRole: controls which cargo gets',
                          canon=[], open_threads=[], changes=['Created all NPC details'])
            failed_ctx, failed_msg, failed_sent = self.request_context(hosted, prompt)
            await hosted['handle_message'](failed_ctx, 'carol', failed_msg)
            self.assertEqual(failed_ctx.storage.values, {})

    async def test_transient_timeout_retries_once_without_saving_twice(self):
        import requests
        hosted = self.load_adapter()
        ctx, msg, sent = self.request_context(hosted, 'Continue from the forged deed sale')
        result = {'adventure':'Baron Hult presents the deed.', 'canon':['The deed was sold'],
                  'open_threads':['Will Hult discover the forgery?'], 'changes':[], 'corrections':[]}
        response = SimpleNamespace(raise_for_status=lambda: None,
            json=lambda: {'choices':[{'message':{'content':json.dumps(result)}}]})
        with patch.dict('os.environ', {'ASI1_API_KEY':'test-only'}), \
                patch('requests.post', side_effect=[requests.Timeout(), response]) as post, \
                patch('time.sleep') as delay:
            await hosted['handle_message'](ctx, 'alice', msg)
        self.assertEqual(post.call_count, 2)
        delay.assert_called_once_with(.5)
        self.assertEqual([c.kwargs['timeout'] for c in post.call_args_list], [(5,40),(5,20)])
        self.assertIn('Baron Hult', sent[-1].content[0].text)
        self.assertEqual(json.loads(next(iter(ctx.storage.values.values())))['state']['turn'], 1)

    async def test_repeated_timeout_stops_after_two_calls_and_preserves_state(self):
        import requests
        hosted = self.load_adapter()
        ctx, msg, sent = self.request_context(hosted, 'Continue')
        with patch.dict('os.environ', {'ASI1_API_KEY':'test-only'}), \
                patch('requests.post', side_effect=requests.Timeout()) as post, patch('time.sleep'):
            await hosted['handle_message'](ctx, 'alice', msg)
        self.assertEqual(post.call_count, 2)
        self.assertEqual(ctx.storage.values, {})
        self.assertIn('try again later', sent[-1].content[0].text)

    async def test_authentication_failure_is_not_retried(self):
        import requests
        hosted = self.load_adapter()
        error = requests.HTTPError(response=SimpleNamespace(status_code=401))
        with patch.dict('os.environ', {'ASI1_API_KEY':'test-only'}), \
                patch('requests.post', side_effect=error) as post, patch('time.sleep') as delay:
            with self.assertRaises(hosted['ModelUnavailable']):
                hosted['hosted_model']([])
        self.assertEqual(post.call_count, 1)
        delay.assert_not_called()

    async def test_provider_requests_schema_and_rejects_bad_envelopes(self):
        hosted = self.load_adapter()
        response = SimpleNamespace(raise_for_status=lambda: None,
            json=lambda: {'choices':[{'finish_reason':'stop', 'message':{'content':'{}'}}]})
        with patch.dict('os.environ', {'ASI1_API_KEY':'test-only',
                                     'ASI1_BASE_URL':'https://api.asi1.ai/v1'}), \
                patch('requests.post', return_value=response) as post:
            self.assertEqual(hosted['hosted_model']([]), '{}')
            body = post.call_args.kwargs['json']
            self.assertEqual(body['response_format']['type'], 'json_schema')
            self.assertTrue(body['response_format']['json_schema']['strict'])
            self.assertEqual(body['reasoning_effort'], 'low')
            response.json = lambda: {'choices':[{'finish_reason':'length',
                                                 'message':{'content':'{"adventure":'}}]}
            with self.assertRaisesRegex(ValueError, 'token limit'):
                hosted['hosted_model']([])
            response.json = lambda: {'choices':[{'message':{'content':''}}]}
            with self.assertRaisesRegex(ValueError, 'empty'):
                hosted['hosted_model']([])
            def bad_http_json():
                raise ValueError('not JSON')
            response.json = bad_http_json
            with self.assertRaisesRegex(ValueError, 'provider-envelope'):
                hosted['hosted_model']([])

    def load_adapter(self):
        class ProtocolStub:
            def __init__(self, **kwargs):
                pass
            def on_message(self, model):
                return lambda handler: handler
        agent = SimpleNamespace(address='agent1example', include=lambda *a, **k: None)
        with patch('uagents.Agent', return_value=agent), patch('uagents.Protocol', ProtocolStub):
            return runpy.run_path(str(ROOT/'hosted/agent.py'))

    def request_context(self, hosted, text):
        sent = []
        async def send(sender, message):
            sent.append(message)
        logger = SimpleNamespace(info=lambda message: None, error=lambda message: None)
        ctx = SimpleNamespace(storage=Storage(), session='one', logger=logger, send=send)
        msg = hosted['ChatMessage'](timestamp=datetime.now(timezone.utc), msg_id=uuid4(),
                                   content=[hosted['TextContent'](type='text', text=text)])
        return ctx, msg, sent

    async def test_timeout_returns_actionable_error_without_saving(self):
        hosted = self.load_adapter()
        ctx, msg, sent = self.request_context(hosted, 'Create an NPC')
        def timeout(messages, audit=None):
            raise hosted['ModelTimeout']('timeout')
        hosted['handle_message'].__globals__['hosted_model'] = timeout
        await hosted['handle_message'](ctx, 'alice', msg)
        self.assertIn('took too long', sent[-1].content[0].text)
        self.assertIn('do not need to create a campaign', sent[-1].content[0].text)
        self.assertEqual(ctx.storage.values, {})

    async def test_model_wait_does_not_block_event_loop(self):
        import asyncio
        import threading
        hosted = self.load_adapter()
        ctx, msg, sent = self.request_context(hosted, 'Create an NPC')
        entered, release = threading.Event(), threading.Event()
        def slow(messages, audit=None):
            entered.set()
            if not release.wait(3):
                raise AssertionError('The event loop did not release the model worker')
            return json.dumps({'adventure':'NPC', 'canon':[], 'open_threads':[], 'changes':[]})
        hosted['handle_message'].__globals__['hosted_model'] = slow
        task = asyncio.create_task(hosted['handle_message'](ctx, 'alice', msg))
        try:
            for _ in range(100):
                if entered.is_set():
                    break
                await asyncio.sleep(.01)
            self.assertTrue(entered.is_set())
        finally:
            release.set()
            await task
        self.assertEqual(sent[-1].content[0].text, 'NPC')

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


class HostedAuditTests(unittest.TestCase):
    def test_audit_distinguishes_status_generation_and_duplicate(self):
        events = []
        storage = Storage()
        def provider(messages):
            return json.dumps({'adventure':'A scene', 'canon':[], 'open_threads':[], 'changes':[]})
        def audit(*event):
            events.append(event)
        process = HOSTED['process_request']
        process(storage,'a','s','one','World','agent1x',provider,audit)
        process(storage,'a','s','one','World','agent1x',provider,audit)
        process(storage,'a','s','two','/status','agent1x',provider,audit)
        self.assertEqual(events, [('generation-start',0,True),('generation-saved',1,True),
                                  ('duplicate-replay',1,False),('status',1,False)])

    def test_broken_diagnostic_does_not_block_reply(self):
        def broken(*args):
            raise RuntimeError('logger unavailable')
        reply = HOSTED['process_request'](Storage(),'a','s','one','/help','agent1x',None,broken)
        self.assertIn('/status',reply)

