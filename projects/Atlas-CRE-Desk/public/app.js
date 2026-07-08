const state = {
  user: null,
  dashboard: null,
  deals: []
};

const elements = {
  login: document.querySelector('#login'),
  workspace: document.querySelector('#workspace'),
  loginForm: document.querySelector('#login-form'),
  loginError: document.querySelector('#login-error'),
  logout: document.querySelector('#logout'),
  userChip: document.querySelector('#user-chip'),
  metrics: document.querySelector('#metrics'),
  deals: document.querySelector('#deals'),
  tasks: document.querySelector('#tasks'),
  riskMix: document.querySelector('#risk-mix'),
  activity: document.querySelector('#activity'),
  stageFilter: document.querySelector('#stage-filter'),
  riskFilter: document.querySelector('#risk-filter'),
  dealForm: document.querySelector('#deal-form')
};

boot();

async function boot() {
  const session = await api('/api/session');
  if (session.user) {
    state.user = session.user;
    showWorkspace();
    await refresh();
  }
}

elements.loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  elements.loginError.value = '';
  const body = Object.fromEntries(new FormData(elements.loginForm));
  try {
    const result = await api('/api/auth/login', { method: 'POST', body });
    state.user = result.user;
    showWorkspace();
    await refresh();
  } catch (error) {
    elements.loginError.value = error.message;
  }
});

elements.logout.addEventListener('click', async () => {
  await api('/api/auth/logout', { method: 'POST' });
  state.user = null;
  elements.workspace.classList.add('hidden');
  elements.logout.classList.add('hidden');
  elements.login.classList.remove('hidden');
});

elements.stageFilter.addEventListener('change', loadDeals);
elements.riskFilter.addEventListener('change', loadDeals);

elements.dealForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const body = Object.fromEntries(new FormData(elements.dealForm));
  await api('/api/deals', { method: 'POST', body });
  elements.dealForm.reset();
  await refresh();
});

function showWorkspace() {
  elements.login.classList.add('hidden');
  elements.workspace.classList.remove('hidden');
  elements.logout.classList.remove('hidden');
  elements.userChip.textContent = `${state.user.name} · ${state.user.role}`;
}

async function refresh() {
  state.dashboard = await api('/api/dashboard');
  renderDashboard();
  await loadDeals();
}

async function loadDeals() {
  const params = new URLSearchParams();
  if (elements.stageFilter.value) params.set('stage', elements.stageFilter.value);
  if (elements.riskFilter.value) params.set('risk', elements.riskFilter.value);
  const result = await api(`/api/deals?${params}`);
  state.deals = result.deals;
  renderDeals();
}

function renderDashboard() {
  const { metrics, riskMix, tasks, activity } = state.dashboard;
  elements.metrics.innerHTML = [
    metric('Active deals', metrics.activeDeals),
    metric('Weighted equity', money(metrics.weightedEquity)),
    metric('Avg target IRR', `${metrics.averageIrr}%`),
    metric('Open tasks', metrics.openTasks)
  ].join('');

  const totalRisk = Object.values(riskMix).reduce((sum, value) => sum + value, 0) || 1;
  elements.riskMix.innerHTML = Object.entries(riskMix)
    .map(([risk, count]) => {
      const width = Math.round((count / totalRisk) * 100);
      return `<div class="mix-item"><span>${risk}</span><div class="bar"><span style="width:${width}%"></span></div><strong>${count}</strong></div>`;
    })
    .join('');

  elements.tasks.innerHTML = tasks
    .map(
      (task) => `<label class="task">
        <input type="checkbox" data-task="${task.id}" ${task.done ? 'checked' : ''} />
        <span><strong>${escapeHtml(task.title)}</strong><small>${task.owner} · Due ${task.due}</small></span>
      </label>`
    )
    .join('');

  elements.tasks.querySelectorAll('[data-task]').forEach((checkbox) => {
    checkbox.addEventListener('change', async () => {
      await api(`/api/tasks/${checkbox.dataset.task}`, { method: 'PATCH', body: { done: checkbox.checked } });
      await refresh();
    });
  });

  elements.activity.innerHTML = activity
    .map((item) => `<div><strong>${escapeHtml(item.label)}</strong><br /><small>${new Date(item.at).toLocaleString()}</small></div>`)
    .join('');
}

function renderDeals() {
  elements.deals.innerHTML = state.deals
    .map(
      (deal) => `<article class="deal-row">
        <div><strong>${escapeHtml(deal.name)}</strong><small>${escapeHtml(deal.market)} · ${escapeHtml(deal.asset)}</small></div>
        <div>${escapeHtml(deal.stage)}<br /><small>${escapeHtml(deal.sponsor)}</small></div>
        <div><strong>${money(deal.equity)}</strong><small>Equity</small></div>
        <div><strong>${deal.irr}%</strong><small>${deal.multiple}x</small></div>
        <span class="badge risk-${deal.risk}">${deal.risk}</span>
      </article>`
    )
    .join('');
}

function metric(label, value) {
  return `<div class="metric"><span class="eyebrow">${label}</span><strong>${value}</strong></div>`;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    method: options.method || 'GET',
    headers: options.body ? { 'Content-Type': 'application/json' } : {},
    body: options.body ? JSON.stringify(options.body) : undefined
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || 'Request failed');
  return payload;
}

function money(value) {
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: 'compact', maximumFractionDigits: 1 }).format(value);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[char]);
}
