export async function storageOperation(storage, body) {
  if (new TextEncoder().encode(JSON.stringify(body.state ?? null)).length > 100000)
    return {error: 'Campaign state too large', status: 413};
  if (body.operation === 'import') {
    if (!body.state || !Number.isSafeInteger(body.state.turn) || body.state.turn < 1 ||
        !Array.isArray(body.state.canon) || !Array.isArray(body.state.open_threads))
      return {error: 'Invalid import', status: 400};
    return storage.transaction(async tx => {
      const current = await tx.get('current');
      if (current) return JSON.stringify(current.state) === JSON.stringify(body.state)
        ? current : {error: 'Import cannot overwrite an existing campaign', status: 409};
      const imported = {revision: 1, state: body.state};
      await tx.put('current', imported);
      return imported;
    });
  }
  if (body.operation === 'read') {
    return storage.transaction(async tx => {
      const current = await tx.get('current') ?? {revision: 0, state: null};
      const reply = body.message_id ? await tx.get(`reply:${body.message_id}`) : null;
      return {...current, reply: reply ?? null};
    });
  }
  if (body.operation !== 'commit' || !Number.isSafeInteger(body.revision) ||
      !body.state || !Number.isSafeInteger(body.state.turn) ||
      !Array.isArray(body.state.canon) || !Array.isArray(body.state.open_threads) ||
      typeof body.fingerprint !== 'string') {
    return {error: 'Invalid operation', status: 400};
  }
  return storage.transaction(async tx => {
    const current = await tx.get('current') ?? {revision: 0, state: null};
    if (body.message_id) {
      const cached = await tx.get(`reply:${body.message_id}`);
      if (cached) return cached.fingerprint === body.fingerprint
        ? {state: cached.state, revision: current.revision}
        : {error: 'Message ID conflict', status: 409};
    }
    if (body.revision !== current.revision) return {error: 'Revision conflict', status: 409};
    if (body.state.turn !== (current.state?.turn ?? 0) + 1) return {error: 'Invalid turn', status: 409};
    const next = {revision: current.revision + 1, state: body.state};
    await tx.put('current', next);
    if (body.message_id) await tx.put(`reply:${body.message_id}`, {
      fingerprint: body.fingerprint, state: body.state
    });
    return next;
  });
}
