import { mkdtemp, rm } from 'node:fs/promises';
import { join } from 'node:path';
import { tmpdir } from 'node:os';
import test from 'node:test';
import assert from 'node:assert/strict';
import { Store } from '../src/data/store.mjs';

test('store loads seed data and computes dashboard metrics', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'atlas-store-'));
  const store = new Store(join(dir, 'data.json'));
  await store.load();

  const dashboard = store.dashboard();
  assert.equal(dashboard.metrics.activeDeals, 4);
  assert.equal(dashboard.metrics.openTasks, 3);
  assert.equal(dashboard.riskMix.Medium, 2);

  await rm(dir, { recursive: true, force: true });
});

test('store validates and persists new deals', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'atlas-store-'));
  const store = new Store(join(dir, 'data.json'));
  await store.load();

  const deal = await store.createDeal({
    name: 'Station Yard',
    market: 'Denver',
    asset: 'Mixed Use',
    stage: 'Screening',
    sponsor: 'Summit',
    equity: 12000000,
    irr: 14.2,
    multiple: 1.7
  });

  assert.equal(deal.name, 'Station Yard');
  assert.equal(store.listDeals({ stage: 'Screening' }).some((item) => item.name === 'Station Yard'), true);

  await rm(dir, { recursive: true, force: true });
});
