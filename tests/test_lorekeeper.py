import asyncio
import copy
import hashlib
import json
import runpy
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from agm.lorekeeper import review_snapshot, parse_review, parse_review_completion
import test_hosted as helpers
from test_hosted import Storage, ROOT


class ReviewContractTests(unittest.TestCase):
    def test_model_verdict_is_derived_in_both_inconsistent_cases(self):
        snapshot = review_snapshot(Storage(), 'a', 's', 'Draft: no memory was lost.')
        finding = {'issue': 'Memory cost missing', 'evidence': 'no memory was lost.',
                   'suggestion': 'Apply the stated cost.'}
        for generated in (None, 'no_conflict_found', 'issues_found'):
            for findings in ([], [finding]):
                value = {'findings': findings, 'notes': []}
                if generated is not None: value['verdict'] = generated
                result = parse_review_completion(json.dumps(value), snapshot)
                self.assertEqual(result['verdict'], 'issues_found' if findings else 'no_conflict_found')

    def test_derived_verdict_still_rejects_ungrounded_or_malformed_findings(self):
        snapshot = review_snapshot(Storage(), 'a', 's', 'A scene')
        for findings in ('not a list', [{'issue': 'issue', 'evidence': 'Invented quote', 'suggestion': 'change'}]):
            with self.assertRaises(ValueError):
                parse_review_completion(json.dumps({'findings': findings, 'notes': []}), snapshot)
    def test_snapshot_is_read_only_and_sender_session_scoped(self):
        store = Storage()
        def provider(_):
            return json.dumps({'adventure': 'A mage casts freely.',
                              'canon': ['Every spell costs a memory.'], 'open_threads': [], 'changes': []})
        hosted = runpy.run_path(str(ROOT/'hosted/agent.py'), init_globals={'_AGM_TEST_MODE': True})
        hosted['process_request'](store, 'alice', 'one', 'm', 'world', 'agent1x', provider)
        before = copy.deepcopy(store.values)
        self.assertIsNone(review_snapshot(store, 'bob', 'one'))
        self.assertIsNone(review_snapshot(store, 'alice', 'two'))
        self.assertIn('A mage casts freely.', review_snapshot(store, 'alice', 'one'))
        self.assertEqual(before, store.values)

    def test_evidence_must_be_grounded_and_verdict_consistent(self):
        snapshot = review_snapshot(Storage(), 'a', 's', 'Rules: spells cost a memory. Draft: no memory was lost.')
        result = {'verdict': 'issues_found', 'findings': [{
            'issue': 'The stated cost is absent.', 'evidence': 'no memory was lost.',
            'suggestion': 'Ask the GM which memory was consumed.'}], 'notes': []}
        self.assertEqual(parse_review(json.dumps(result), snapshot), result)
        result['findings'][0]['evidence'] = 'invented evidence'
        with self.assertRaisesRegex(ValueError, 'exact source quote'):
            parse_review(json.dumps(result), snapshot)
        result['findings'] = []
        with self.assertRaisesRegex(ValueError, 'contradicts'):
            parse_review(json.dumps(result), snapshot)

    def test_bounded_payloads_and_nonobject_results_rejected(self):
        with self.assertRaises(ValueError):
            review_snapshot(Storage(), 'a', 's', 'x'*8001)
        snapshot = review_snapshot(Storage(), 'a', 's', 'A scene')
        with self.assertRaises(ValueError):
            parse_review('[]', snapshot)

    def test_standalone_rules_and_draft_are_explicit_review_material(self):
        snapshot = json.loads(review_snapshot(Storage(), 'a', 's', 'Rules: magic costs memories. Draft: No memory was lost.'))
        self.assertEqual(snapshot['draft'], 'No memory was lost.')
        self.assertEqual(snapshot['canon'], ['Rules: magic costs memories.'])
        self.assertEqual(snapshot['gm_review_brief'], '')


class ReviewAdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_visible_handle_review_routes_to_peer_without_story_generation(self):
        hosted, ctx, msg, sent = self.adapter()
        msg.content[0].text = '@agenticgamemaster /review Rules: Every spell permanently consumes one memory of its caster. Draft: A mage casts three spells. No memory was lost, and there was no exception to the rule.'
        calls = []
        async def exchange(peer, request, response_type, timeout):
            calls.append(request)
            snapshot = json.loads(request.snapshot_json)
            self.assertEqual(snapshot['draft'], 'A mage casts three spells. No memory was lost, and there was no exception to the rule.')
            return response_type(request_id=request.request_id,
                snapshot_hash=hashlib.sha256(request.snapshot_json.encode()).hexdigest(),
                report_json=json.dumps({'verdict': 'issues_found', 'findings': [{
                    'issue': 'Memory cost is missing', 'evidence': 'No memory was lost',
                    'suggestion': 'One memory per spell, three memories total.'}], 'notes': []}), error=''), None
        ctx.send_and_receive = exchange
        with patch('requests.post', side_effect=AssertionError('This command must not call the story model')):
            await hosted['handle_message'](ctx, 'alice', msg)
        self.assertEqual(len(calls), 1)
        self.assertIn('## Lorekeeper review', sent[-1].content[0].text)
        self.assertEqual(ctx.storage.values, {})

    async def test_visible_handle_status_is_deterministic_without_model_or_state_write(self):
        hosted, ctx, msg, sent = self.adapter()
        msg.content[0].text = '@agenticgamemaster /status'
        with patch('requests.post', side_effect=AssertionError('Status must not call the story model')):
            await hosted['handle_message'](ctx, 'alice', msg)
        self.assertEqual(sent[-1].content[0].text, 'No campaign in this conversation yet. Describe your world to begin.')
        self.assertEqual(ctx.storage.values, {})

    def adapter(self):
        helper = helpers.HostedAdapterTests()
        hosted = helper.load_adapter()
        hosted['request_lore_review'].__globals__['LOREKEEPER_ADDRESS'] = 'agent1reviewer'
        ctx, msg, sent = helper.request_context(hosted, '/review Rules: spells cost memories. Draft: no memory was lost.')
        return hosted, ctx, msg, sent

    async def test_real_typed_request_response_path_without_campaign_mutation(self):
        hosted, ctx, msg, sent = self.adapter()
        report = {'verdict': 'issues_found', 'findings': [{
            'issue': 'Spell cost missing', 'evidence': 'no memory was lost.',
            'suggestion': 'Apply the established memory cost.'}], 'notes': []}
        async def exchange(peer, request, response_type, timeout):
            self.assertEqual(peer, 'agent1reviewer')
            return response_type(request_id=request.request_id,
                snapshot_hash=hashlib.sha256(request.snapshot_json.encode()).hexdigest(),
                report_json=json.dumps(report), error=''), None
        ctx.send_and_receive = exchange
        with patch('requests.post', side_effect=AssertionError('AGM review must not call its story model')):
            await hosted['handle_message'](ctx, 'alice', msg)
        self.assertIn('Spell cost missing', sent[-1].content[0].text)
        self.assertIn('GM only', sent[-1].content[0].text)
        self.assertEqual(ctx.storage.values, {})

    async def test_mismatched_or_missing_response_never_claims_review(self):
        for kind in ('id', 'snapshot', 'missing', 'error', 'unquoted'):
            hosted, ctx, msg, sent = self.adapter()
            async def exchange(peer, request, response_type, timeout):
                if kind == 'missing': return None, None
                report = {'verdict': 'no_conflict_found', 'findings': [], 'notes': []}
                if kind == 'unquoted': report = {'verdict': 'issues_found', 'findings': [{
                    'issue': 'issue', 'evidence': 'invented', 'suggestion': 'change'}], 'notes': []}
                return response_type(request_id='wrong' if kind == 'id' else request.request_id,
                    snapshot_hash='wrong' if kind == 'snapshot' else hashlib.sha256(request.snapshot_json.encode()).hexdigest(),
                    report_json=json.dumps(report), error='unavailable' if kind == 'error' else ''), None
            ctx.send_and_receive = exchange
            await hosted['handle_message'](ctx, 'alice', msg)
            self.assertIn('no review is claimed', sent[-1].content[0].text)
            self.assertEqual(ctx.storage.values, {})

    async def test_timeout_fails_open_and_normal_commands_stay_available(self):
        hosted, ctx, msg, sent = self.adapter()
        async def exchange(*args, **kwargs): raise asyncio.TimeoutError()
        ctx.send_and_receive = exchange
        await hosted['handle_message'](ctx, 'alice', msg)
        self.assertIn('continue playing', sent[-1].content[0].text)
        self.assertEqual(ctx.storage.values, {})

    async def test_empty_review_does_not_contact_peer(self):
        hosted, ctx, msg, sent = self.adapter()
        msg.content[0].text = '/review'
        await hosted['handle_message'](ctx, 'alice', msg)
        self.assertIn('Create an NPC', sent[-1].content[0].text)

    async def test_lorekeeper_only_accepts_configured_gm(self):
        class ProtocolStub:
            def __init__(self, **kwargs): pass
            def on_message(self, *args, **kwargs): return lambda f: f
        agent = SimpleNamespace(address='agent1reviewer', include=lambda *a, **k: None)
        with patch('uagents.Agent', return_value=agent), patch('uagents.Protocol', ProtocolStub):
            lore = runpy.run_path(str(ROOT/'hosted/lorekeeper.py'))
        sent = []
        async def send(peer, response): sent.append(response)
        ctx = SimpleNamespace(logger=SimpleNamespace(info=lambda x: None, error=lambda x: None), send=send)
        request = lore['LoreReviewRequest'](request_id='m', snapshot_json=review_snapshot(Storage(), 'a', 's', 'A scene'))
        lore['handle_review'].__globals__['review_model'] = lambda s: json.dumps({'verdict': 'no_conflict_found', 'findings': [], 'notes': []})
        await lore['handle_review'](ctx, 'untrusted', request)
        self.assertEqual(sent, [])
        await lore['handle_review'](ctx, lore['ALLOWED_GM_ADDRESS'], request)
        self.assertEqual(len(sent), 1)
        self.assertEqual(sent[0].error, '')
        self.assertEqual(sent[0].snapshot_hash, hashlib.sha256(request.snapshot_json.encode()).hexdigest())


class ReviewModelRepairTests(unittest.TestCase):
    def load_model(self):
        agent = SimpleNamespace(address='agent1reviewer', include=lambda *a, **k: None)
        with patch('uagents.Agent', return_value=agent):
            return runpy.run_path(str(ROOT/'hosted/lorekeeper.py'))['review_model']

    def test_one_validation_repair_accepts_only_grounded_result(self):
        model = self.load_model()
        snapshot = review_snapshot(Storage(), 'a', 's', 'Draft: no memory was lost.')
        valid = {'verdict': 'issues_found', 'findings': [{'issue': 'Review cost',
            'evidence': 'no memory was lost.', 'suggestion': 'Ask the GM to apply the stated cost.'}], 'notes': []}
        def response(content):
            return SimpleNamespace(raise_for_status=lambda: None, json=lambda: {
                'choices': [{'finish_reason': 'stop', 'message': {'content': content}}]})
        with patch.dict('os.environ', {'ASI1_API_KEY': 'test-only'}), patch('requests.post',
                side_effect=[response('[]'), response(json.dumps(valid))]) as post:
            self.assertEqual(json.loads(model(snapshot)), valid)
        self.assertEqual(post.call_count, 2)
        self.assertEqual(post.call_args.kwargs['timeout'][0], 2)
        self.assertIn('failed validation', post.call_args.kwargs['json']['messages'][-1]['content'])

    def test_repair_is_bounded_and_cannot_accept_fabricated_evidence(self):
        model = self.load_model()
        snapshot = review_snapshot(Storage(), 'a', 's', 'A scene')
        invalid = json.dumps({'verdict': 'issues_found', 'findings': [{'issue': 'Wrong',
            'evidence': 'Fabricated quote', 'suggestion': 'Invent a change'}], 'notes': []})
        response = SimpleNamespace(raise_for_status=lambda: None, json=lambda: {
            'choices': [{'finish_reason': 'stop', 'message': {'content': invalid}}]})
        with patch.dict('os.environ', {'ASI1_API_KEY': 'test-only'}), patch('requests.post', return_value=response) as post:
            with self.assertRaisesRegex(ValueError, 'exact source quote'):
                model(snapshot)
        self.assertEqual(post.call_count, 2)
