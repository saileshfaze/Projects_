import test from 'node:test';
import assert from 'node:assert/strict';
import { createAuth, parseCookies } from '../src/security/auth.mjs';

test('signed sessions verify valid tokens and reject tampering', () => {
  const auth = createAuth({ secret: 'test-secret', ttlMs: 1000 });
  const token = auth.sign({ sub: 'usr_1', name: 'Ava' });

  assert.equal(auth.verify(token).sub, 'usr_1');
  assert.equal(auth.verify(`${token.slice(0, -1)}x`), null);
});

test('cookie parser handles multiple cookies', () => {
  assert.deepEqual(parseCookies('a=1; atlas_session=abc.def'), {
    a: '1',
    atlas_session: 'abc.def'
  });
});
