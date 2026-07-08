import { mkdtemp, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import test from 'node:test';
import assert from 'node:assert/strict';
import { Store } from '../src/data/store.mjs';
import { createApp } from '../src/server.mjs';
import { createAuth } from '../src/security/auth.mjs';

test('api requires authentication and supports login', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'atlas-api-'));
  const server = await createApp({
    appStore: new Store(join(dir, 'data.json')),
    appAuth: createAuth({ secret: 'api-test' })
  });

  await new Promise((resolve) => server.listen(0, resolve));
  const base = `http://127.0.0.1:${server.address().port}`;

  const denied = await fetch(`${base}/api/dashboard`);
  assert.equal(denied.status, 401);

  const login = await fetch(`${base}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: 'analyst@atlas.local', password: 'demo-password' })
  });
  assert.equal(login.status, 200);

  const cookie = login.headers.get('set-cookie');
  const dashboard = await fetch(`${base}/api/dashboard`, { headers: { cookie } });
  assert.equal(dashboard.status, 200);
  assert.equal((await dashboard.json()).metrics.activeDeals, 4);

  server.close();
  await rm(dir, { recursive: true, force: true });
});
