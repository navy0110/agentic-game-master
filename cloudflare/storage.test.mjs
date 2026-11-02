import test from 'node:test';
import assert from 'node:assert/strict';
import {storageOperation} from './storage.mjs';

function memoryStorage() {
  const values = new Map();
  return {get: async key => structuredClone(values.get(key)),
    put: async (key, value) => {values.set(key, structuredClone(value));},
    transaction: async function(fn) {return fn(this);}};
}
const state = turn => ({turn, canon: ['The tower is dark'], open_threads: ['Relight it?']});

test('state survives client restart; duplicate commit replays without overwriting newer state', async () => {
  const storage = memoryStorage();
  assert.equal((await storageOperation(storage, {operation: 'read'})).state, null);
  const first = {operation: 'commit', revision: 0, state: state(1), message_id: 'a', fingerprint: 'hash-a'};
  assert.equal((await storageOperation(storage, first)).revision, 1);
  await storageOperation(storage, {...first, revision: 1, state: state(2), message_id: 'b', fingerprint: 'hash-b'});
  assert.equal((await storageOperation(storage, first)).state.turn, 1);
  const snapshot = await storageOperation(storage, {operation: 'read', message_id: 'a'});
  assert.equal(snapshot.state.turn, 2);
  assert.equal(snapshot.reply.state.turn, 1);
});

test('stale writers and conflicting message IDs cannot corrupt stored state', async () => {
  const storage = memoryStorage();
  const first = {operation: 'commit', revision: 0, state: state(1), message_id: 'a', fingerprint: 'hash-a'};
  await storageOperation(storage, first);
  assert.equal((await storageOperation(storage, {...first, message_id: 'b'})).status, 409);
  assert.equal((await storageOperation(storage, {...first, fingerprint: 'different'})).status, 409);
  assert.equal((await storageOperation(storage, {operation: 'read'})).state.turn, 1);
});

test('ordinary commits must advance exactly one turn', async () => {
  const storage = memoryStorage();
  assert.equal((await storageOperation(storage, {operation: 'commit', revision: 0,
    state: state(4), fingerprint: 'h'})).status, 409);
});

test('campaign import is idempotent and refuses to replace different history', async () => {
  const storage = memoryStorage();
  const imported = await storageOperation(storage, {operation: 'import', state: state(5)});
  assert.equal(imported.state.turn, 5);
  assert.equal((await storageOperation(storage, {operation: 'import', state: state(5)})).revision, 1);
  assert.equal((await storageOperation(storage, {operation: 'import', state: state(2)})).status, 409);
  assert.equal((await storageOperation(storage, {operation: 'read'})).state.turn, 5);
});
