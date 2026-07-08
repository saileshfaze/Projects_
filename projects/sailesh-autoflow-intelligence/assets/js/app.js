const formatCurrency = (value) =>
  new Intl.NumberFormat("en-IE", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(value);

const getJson = async (url) => {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Request failed: ${url}`);
  return response.json();
};

const kpiGrid = document.querySelector("#kpiGrid");
const vehicleGrid = document.querySelector("#vehicleGrid");
const inventoryFilters = document.querySelector("#inventoryFilters");
const leadFilter = document.querySelector("#leadFilter");
const leadTable = document.querySelector("#leadTable");
const assistantList = document.querySelector("#assistantList");
const assistantSummary = document.querySelector("#assistantSummary");
const revenueChart = document.querySelector("#revenueChart");

function renderKpis(kpis) {
  kpiGrid.innerHTML = kpis
    .map(
      (kpi, index) => `
        <article class="kpi-card" style="animation-delay:${index * 80}ms">
          <span class="eyebrow">${kpi.label}</span>
          <strong>${kpi.value}</strong>
          <span class="trend">${kpi.trend}</span>
        </article>
      `
    )
    .join("");
}

function renderHeroInventory(inventory) {
  document.querySelector("#availableCount").textContent = inventory.available;
  document.querySelector("#reservedCount").textContent = inventory.reserved;
  document.querySelector("#averagePrice").textContent = inventory.averagePrice.replace("EUR ", "€");
}

function renderVehicles(items) {
  if (!items.length) {
    vehicleGrid.innerHTML = `<div class="panel"><h3>No vehicles found</h3><p class="muted">Try changing the search or filters.</p></div>`;
    return;
  }

  vehicleGrid.innerHTML = items
    .map(
      (vehicle, index) => `
        <article class="vehicle-card" style="animation-delay:${index * 70}ms">
          <img src="${vehicle.image}" alt="${vehicle.brand} ${vehicle.model}">
          <div class="vehicle-body">
            <div class="vehicle-top">
              <div>
                <h3>${vehicle.brand} ${vehicle.model}</h3>
                <p class="vehicle-meta">${vehicle.year} • ${vehicle.category} • ${vehicle.fuelType}</p>
              </div>
              <span class="badge">${vehicle.status}</span>
            </div>
            <div class="price">${formatCurrency(vehicle.price)}</div>
            <div class="vehicle-stats">
              <span><strong>${vehicle.mileage.toLocaleString()}</strong><small> km</small></span>
              <span><strong>${vehicle.daysInStock}</strong><small> days</small></span>
              <span><strong>${formatCurrency(vehicle.margin)}</strong><small> margin</small></span>
            </div>
          </div>
        </article>
      `
    )
    .join("");
}

async function loadInventory() {
  const params = new URLSearchParams(new FormData(inventoryFilters));
  const data = await getJson(`api/inventory.php?${params}`);
  renderVehicles(data.items);
}

function renderLeads(items) {
  leadTable.innerHTML = items
    .map((lead) => {
      const tempClass = lead.temperature.toLowerCase();
      return `
        <article class="lead-row">
          <div>
            <strong>${lead.customerName}</strong>
            <span>${lead.preferredVehicle} • ${lead.source}</span>
          </div>
          <div>
            <strong>${formatCurrency(lead.budget)}</strong>
            <span>${lead.status}</span>
          </div>
          <div>
            <strong>${lead.nextAction}</strong>
            <span>Owner: ${lead.assignedTo}</span>
          </div>
          <span class="badge temperature ${tempClass}">${lead.temperature}</span>
        </article>
      `;
    })
    .join("");
}

async function loadLeads() {
  const data = await getJson(`api/leads.php?temperature=${leadFilter.value}`);
  renderLeads(data.items);
}

function renderChart(targets) {
  const max = Math.max(...targets.map((item) => item.actual));
  revenueChart.innerHTML = targets
    .map((item) => {
      const height = Math.max(14, Math.round((item.actual / max) * 100));
      return `
        <div class="bar-wrap">
          <span class="bar-label">${item.month}</span>
          <div class="bar" style="height:${height}%" data-value="${formatCurrency(item.actual)}"></div>
        </div>
      `;
    })
    .join("");
}

async function loadAssistant() {
  assistantList.innerHTML = "";
  assistantSummary.textContent = "Analyzing inventory age, lead temperature, and deal status...";
  const data = await getJson("api/assistant.php");
  assistantSummary.textContent = data.summary;
  assistantList.innerHTML = data.recommendations
    .map(
      (item) => `
        <article class="assistant-item">
          <h3>${item.title}</h3>
          <p>${item.detail}</p>
          <small>${item.impact}</small>
        </article>
      `
    )
    .join("");
}

async function loadOverview() {
  const data = await getJson("api/overview.php");
  renderKpis(data.kpis);
  renderHeroInventory(data.inventory);
  renderChart(data.targets);
  document.querySelector("#targetProgress").textContent = data.kpis[3].value;
}

function setActiveNav() {
  const links = [...document.querySelectorAll(".nav-links a")];
  const sections = links
    .map((link) => document.querySelector(link.getAttribute("href")))
    .filter(Boolean);

  const current = sections
    .slice()
    .reverse()
    .find((section) => section.getBoundingClientRect().top < 180);

  if (!current) return;
  links.forEach((link) => link.classList.toggle("active", link.getAttribute("href") === `#${current.id}`));
}

inventoryFilters.addEventListener("input", loadInventory);
leadFilter.addEventListener("change", loadLeads);
document.querySelector("#refreshAssistant").addEventListener("click", loadAssistant);
window.addEventListener("scroll", setActiveNav, { passive: true });

Promise.all([loadOverview(), loadInventory(), loadLeads(), loadAssistant()]).catch((error) => {
  console.error(error);
  document.body.insertAdjacentHTML(
    "afterbegin",
    `<div class="panel" style="margin:16px">Unable to load dashboard data. Please run with PHP local server.</div>`
  );
});

