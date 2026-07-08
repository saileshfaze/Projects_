import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import { createServer } from 'node:http';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Store, ValidationError } from './data/store.mjs';
import { clearSessionCookie, createAuth, makeRequestId, parseCookies, sessionCookie } from './security/auth.mjs';

const root = fileURLToPath(new URL('..', import.meta.url));
const publicDir = join(root, 'public');
const dataPath = process.env.DATA_PATH || join(root, 'data', 'atlas.json');
const port = Number(process.env.PORT || 4173);
const store = new Store(dataPath);
const auth = createAuth();

const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml'
};

export async function createApp({ appStore = store, appAuth = auth } = {}) {
  await appStore.load();

  return createServer(async (req, res) => {
    req.id = makeRequestId();
    try {
      if (req.url.startsWith('/api/')) {
        await handleApi(req, res, appStore, appAuth);
        return;
      }
      await serveStatic(req, res);
    } catch (error) {
      const statusCode = error.statusCode || 500;
      respond(res, statusCode, { error: statusCode === 500 ? 'Unexpected server error' : error.message, requestId: req.id });
      if (statusCode === 500) console.error(`[${req.id}]`, error);
    }
  });
}

async function handleApi(req, res, appStore, appAuth) {
  const url = new URL(req.url, 'http://localhost');
  const user = currentUser(req, appAuth);

  if (req.method === 'POST' && url.pathname === '/api/auth/login') {
    const body = await readJson(req);
    const account = appStore.findUser(body.email, body.password);
    if (!account) return respond(res, 401, { error: 'Invalid email or password' });
    const token = appAuth.sign({ sub: account.id, name: account.name, email: account.email, role: account.role });
    return respond(res, 200, { user: publicUser(account) }, { 'Set-Cookie': sessionCookie(token) });
  }

  if (req.method === 'POST' && url.pathname === '/api/auth/logout') {
    return respond(res, 200, { ok: true }, { 'Set-Cookie': clearSessionCookie() });
  }

  if (req.method === 'GET' && url.pathname === '/api/session') {
    return respond(res, 200, { user });
  }

  if (!user) return respond(res, 401, { error: 'Authentication required' });

  if (req.method === 'GET' && url.pathname === '/api/dashboard') {
    return respond(res, 200, appStore.dashboard());
  }

  if (req.method === 'GET' && url.pathname === '/api/deals') {
    return respond(res, 200, { deals: appStore.listDeals(Object.fromEntries(url.searchParams)) });
  }

  if (req.method === 'POST' && url.pathname === '/api/deals') {
    const deal = await appStore.createDeal(await readJson(req));
    return respond(res, 201, { deal });
  }

  const dealMatch = url.pathname.match(/^\/api\/deals\/([^/]+)$/);
  if (req.method === 'PATCH' && dealMatch) {
    const deal = await appStore.updateDeal(dealMatch[1], await readJson(req));
    if (!deal) return respond(res, 404, { error: 'Deal not found' });
    return respond(res, 200, { deal });
  }

  const taskMatch = url.pathname.match(/^\/api\/tasks\/([^/]+)$/);
  if (req.method === 'PATCH' && taskMatch) {
    const task = await appStore.updateTask(taskMatch[1], await readJson(req));
    if (!task) return respond(res, 404, { error: 'Task not found' });
    return respond(res, 200, { task });
  }

  respond(res, 404, { error: 'Route not found' });
}

function currentUser(req, appAuth) {
  const cookies = parseCookies(req.headers.cookie || '');
  const payload = appAuth.verify(cookies[appAuth.cookieName]);
  if (!payload) return null;
  return { id: payload.sub, name: payload.name, email: payload.email, role: payload.role };
}

async function serveStatic(req, res) {
  const url = new URL(req.url, 'http://localhost');
  const requested = url.pathname === '/' ? '/index.html' : url.pathname;
  const safePath = normalize(decodeURIComponent(requested)).replace(/^(\.\.[/\\])+/, '');
  const filePath = join(publicDir, safePath);
  if (!filePath.startsWith(publicDir)) return respond(res, 403, { error: 'Forbidden' });

  try {
    const file = await stat(filePath);
    if (!file.isFile()) throw Object.assign(new Error('Not found'), { code: 'ENOENT' });
    res.writeHead(200, {
      'Content-Type': mimeTypes[extname(filePath)] || 'application/octet-stream',
      'Cache-Control': 'no-store'
    });
    createReadStream(filePath).pipe(res);
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
    res.writeHead(302, { Location: '/' });
    res.end();
  }
}

async function readJson(req) {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  if (!chunks.length) return {};
  try {
    return JSON.parse(Buffer.concat(chunks).toString('utf8'));
  } catch {
    throw Object.assign(new Error('Invalid JSON body'), { statusCode: 400 });
  }
}

function respond(res, statusCode, payload, headers = {}) {
  res.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'X-Content-Type-Options': 'nosniff',
    ...headers
  });
  res.end(JSON.stringify(payload));
}

function publicUser(user) {
  return { id: user.id, name: user.name, email: user.email, role: user.role };
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  const server = await createApp();
  server.listen(port, () => {
    console.log(`Atlas CRE Desk running at http://localhost:${port}`);
  });
}

export { ValidationError };
