import { DurableObject } from 'cloudflare:workers';
import { storageOperation } from './storage.mjs';

export class CampaignStore extends DurableObject {
  async fetch(request) {
    const body = await request.json();
    const result = await storageOperation(this.ctx.storage, body);
    return Response.json(result, {status: result.status ?? 200});
  }
}

export class GameMasterRuntime extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    if (ctx.container?.running) ctx.blockConcurrencyWhile(() => ctx.container.setInactivityTimeout(300000));
  }
  async ensureRunning() {
    if (this.env.AGM_ENABLED !== 'true') return {enabled: false, running: false};
    const c = this.ctx.container;
    if (!c) throw new Error('Container binding missing');
    if (!c.running) {
      if (!this.env.AGM_PUBLIC_URL?.startsWith('https://') ||
          !this.env.ASI_ONE_API_KEY || !this.env.AGENT_SEED || !this.env.AGM_STORAGE_TOKEN) {
        throw new Error('Set the Worker URL and required secrets before enabling the runtime');
      }
      c.start({image: c.images.base, instance: 'lite', enableInternet: true, env: {
        ASI_ONE_API_KEY: this.env.ASI_ONE_API_KEY,
        ASI_ONE_MODEL: this.env.ASI_ONE_MODEL ?? 'asi1',
        AGENT_SEED: this.env.AGENT_SEED,
        AGM_STORAGE_URL: this.env.AGM_PUBLIC_URL,
        AGM_STORAGE_TOKEN: this.env.AGM_STORAGE_TOKEN,
        AGENT_PORT: '8001'
      }});
    }
    await c.setInactivityTimeout(300000);
    return {enabled: true, running: c.running};
  }
  async fetch() {
    const runtime = await this.ensureRunning();
    if (!runtime.running) return Response.json(runtime);
    // Report readiness separately: a running container may still be booting.
    try {
      const response = await this.ctx.container.getTcpPort(8001).fetch('http://container/agent_info',
        {signal: AbortSignal.timeout(5000)});
      return Response.json({...runtime, ready: response.ok});
    } catch {
      return Response.json({...runtime, ready: false}, {status: 503});
    }
  }
}

export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname;
    if (path === '/health' && request.method === 'GET') {
      return Response.json({service: 'Agentic Game Master', storage: 'Durable Objects',
        enabled: env.AGM_ENABLED === 'true'});
    }
    // No public forwarding to /connect, /disconnect, inspector, or campaign data.
    if (!['/internal/storage', '/admin/runtime'].includes(path)) return new Response('Not found', {status: 404});
    if (!env.AGM_STORAGE_TOKEN || request.headers.get('authorization') !== `Bearer ${env.AGM_STORAGE_TOKEN}`)
      return new Response('Unauthorized', {status: 401});
    if (request.method !== 'POST') return new Response('Method not allowed', {status: 405});
    if (path === '/admin/runtime') return env.RUNTIME.getByName('primary').fetch(request);
    const raw = await request.text();
    if (new TextEncoder().encode(raw).length > 500000) return new Response('Too large', {status: 413});
    let body;
    try { body = JSON.parse(raw); } catch { return new Response('Invalid JSON', {status: 400}); }
    if (typeof body.owner !== 'string' || typeof body.session !== 'string' ||
        !body.owner || !body.session || body.owner.length > 256 || body.session.length > 256 ||
        (body.message_id != null && (typeof body.message_id !== 'string' || body.message_id.length > 128)))
      return new Response('Invalid campaign identity', {status: 400});
    const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify([body.owner, body.session])));
    const key = Array.from(new Uint8Array(digest), b => b.toString(16).padStart(2, '0')).join('');
    return env.CAMPAIGNS.getByName(key).fetch(new Request('https://storage/operation', {
      method: 'POST', body: raw, headers: {'content-type': 'application/json'}
    }));
  },
  async scheduled(_event, env, ctx) {
    if (env.AGM_ENABLED === 'true') ctx.waitUntil(env.RUNTIME.getByName('primary').ensureRunning());
  }
};
