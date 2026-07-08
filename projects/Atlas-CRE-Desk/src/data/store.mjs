import { mkdir, readFile, rename, writeFile } from 'node:fs/promises';
import { dirname } from 'node:path';
import { randomUUID } from 'node:crypto';

const seed = {
  users: [
    {
      id: 'usr_analyst',
      name: 'Maya Chen',
      email: 'analyst@atlas.local',
      password: 'demo-password',
      role: 'Acquisitions Lead'
    }
  ],
  deals: [
    {
      id: 'deal_rivergate',
      name: 'Rivergate Logistics Park',
      market: 'Dallas-Fort Worth',
      asset: 'Industrial',
      stage: 'IC Memo',
      sponsor: 'Northline Capital',
      equity: 42500000,
      irr: 18.4,
      multiple: 2.1,
      risk: 'Medium',
      nextMilestone: 'Investment committee vote',
      closeDate: '2026-08-21',
      updatedAt: '2026-07-08T12:40:00.000Z'
    },
    {
      id: 'deal_harbor',
      name: 'Harbor Lofts',
      market: 'San Diego',
      asset: 'Multifamily',
      stage: 'Diligence',
      sponsor: 'Crescent Urban',
      equity: 31000000,
      irr: 15.7,
      multiple: 1.8,
      risk: 'Low',
      nextMilestone: 'Environmental report review',
      closeDate: '2026-09-04',
      updatedAt: '2026-07-07T16:05:00.000Z'
    },
    {
      id: 'deal_civic',
      name: 'Civic Center Medical Offices',
      market: 'Phoenix',
      asset: 'Healthcare',
      stage: 'LOI',
      sponsor: 'Verde Health Properties',
      equity: 22500000,
      irr: 16.9,
      multiple: 1.9,
      risk: 'Medium',
      nextMilestone: 'Seller call on lease rollover',
      closeDate: '2026-10-16',
      updatedAt: '2026-07-06T20:15:00.000Z'
    },
    {
      id: 'deal_meridian',
      name: 'Meridian Cold Storage',
      market: 'Atlanta',
      asset: 'Cold Storage',
      stage: 'Screening',
      sponsor: 'Everlane Partners',
      equity: 56000000,
      irr: 19.8,
      multiple: 2.3,
      risk: 'High',
      nextMilestone: 'Power capacity diligence',
      closeDate: '2026-11-12',
      updatedAt: '2026-07-05T09:25:00.000Z'
    }
  ],
  tasks: [
    { id: 'task_1', dealId: 'deal_rivergate', title: 'Refresh debt quotes with downside case', owner: 'Maya', due: '2026-07-10', done: false },
    { id: 'task_2', dealId: 'deal_harbor', title: 'Confirm seismic scope with engineer', owner: 'Noah', due: '2026-07-11', done: false },
    { id: 'task_3', dealId: 'deal_civic', title: 'Summarize top five tenant rollover risks', owner: 'Priya', due: '2026-07-09', done: true },
    { id: 'task_4', dealId: 'deal_meridian', title: 'Build energy sensitivity table', owner: 'Maya', due: '2026-07-14', done: false }
  ],
  activity: [
    { id: 'act_1', label: 'Rivergate IC memo moved to final review', at: '2026-07-08T12:40:00.000Z' },
    { id: 'act_2', label: 'Harbor Lofts diligence checklist updated', at: '2026-07-07T16:05:00.000Z' },
    { id: 'act_3', label: 'Civic Center lease abstract uploaded', at: '2026-07-06T20:15:00.000Z' }
  ]
};

export class Store {
  constructor(filePath) {
    this.filePath = filePath;
    this.data = structuredClone(seed);
  }

  async load() {
    try {
      this.data = JSON.parse(await readFile(this.filePath, 'utf8'));
    } catch (error) {
      if (error.code !== 'ENOENT') throw error;
      await this.save();
    }
  }

  async save() {
    await mkdir(dirname(this.filePath), { recursive: true });
    const tempPath = `${this.filePath}.${process.pid}.tmp`;
    await writeFile(tempPath, JSON.stringify(this.data, null, 2));
    await rename(tempPath, this.filePath);
  }

  findUser(email, password) {
    const normalized = String(email || '').toLowerCase();
    return this.data.users.find((user) => user.email === normalized && user.password === password) || null;
  }

  dashboard() {
    const activeDeals = this.data.deals.filter((deal) => deal.stage !== 'Closed');
    const weightedEquity = activeDeals.reduce((sum, deal) => sum + deal.equity, 0);
    const averageIrr = activeDeals.reduce((sum, deal) => sum + deal.irr, 0) / Math.max(activeDeals.length, 1);
    const urgentTasks = this.data.tasks
      .filter((task) => !task.done)
      .sort((a, b) => a.due.localeCompare(b.due));

    return {
      metrics: {
        activeDeals: activeDeals.length,
        weightedEquity,
        averageIrr: Number(averageIrr.toFixed(1)),
        openTasks: urgentTasks.length
      },
      stageMix: groupCount(activeDeals, 'stage'),
      riskMix: groupCount(activeDeals, 'risk'),
      tasks: urgentTasks,
      activity: this.data.activity.slice(0, 8)
    };
  }

  listDeals(filters = {}) {
    return this.data.deals
      .filter((deal) => !filters.stage || deal.stage === filters.stage)
      .filter((deal) => !filters.risk || deal.risk === filters.risk)
      .sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
  }

  async createDeal(input) {
    const deal = normalizeDeal(input);
    this.data.deals.unshift({ ...deal, id: `deal_${randomUUID()}`, updatedAt: new Date().toISOString() });
    this.record(`${deal.name} added to ${deal.stage}`);
    await this.save();
    return this.data.deals[0];
  }

  async updateDeal(id, patch) {
    const deal = this.data.deals.find((item) => item.id === id);
    if (!deal) return null;
    const allowed = ['stage', 'risk', 'nextMilestone', 'irr', 'multiple', 'equity', 'closeDate'];
    for (const key of allowed) {
      if (patch[key] !== undefined) deal[key] = patch[key];
    }
    deal.updatedAt = new Date().toISOString();
    this.record(`${deal.name} updated`);
    await this.save();
    return deal;
  }

  async updateTask(id, patch) {
    const task = this.data.tasks.find((item) => item.id === id);
    if (!task) return null;
    task.done = Boolean(patch.done);
    this.record(`${task.title} marked ${task.done ? 'complete' : 'open'}`);
    await this.save();
    return task;
  }

  record(label) {
    this.data.activity.unshift({ id: `act_${randomUUID()}`, label, at: new Date().toISOString() });
    this.data.activity = this.data.activity.slice(0, 20);
  }
}

function groupCount(items, key) {
  return items.reduce((groups, item) => {
    groups[item[key]] = (groups[item[key]] || 0) + 1;
    return groups;
  }, {});
}

function normalizeDeal(input) {
  const required = ['name', 'market', 'asset', 'stage', 'sponsor'];
  for (const field of required) {
    if (!String(input[field] || '').trim()) {
      throw new ValidationError(`${field} is required`);
    }
  }

  return {
    name: String(input.name).trim(),
    market: String(input.market).trim(),
    asset: String(input.asset).trim(),
    stage: String(input.stage).trim(),
    sponsor: String(input.sponsor).trim(),
    equity: toNumber(input.equity, 'equity'),
    irr: toNumber(input.irr, 'irr'),
    multiple: toNumber(input.multiple, 'multiple'),
    risk: String(input.risk || 'Medium'),
    nextMilestone: String(input.nextMilestone || 'Initial review'),
    closeDate: String(input.closeDate || new Date().toISOString().slice(0, 10))
  };
}

function toNumber(value, field) {
  const number = Number(value);
  if (!Number.isFinite(number) || number < 0) throw new ValidationError(`${field} must be a positive number`);
  return number;
}

export class ValidationError extends Error {
  constructor(message) {
    super(message);
    this.name = 'ValidationError';
    this.statusCode = 422;
  }
}
