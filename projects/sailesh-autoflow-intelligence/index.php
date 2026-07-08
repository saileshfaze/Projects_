<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AutoFlow Intelligence</title>
  <meta name="description" content="Full-stack automotive sales, inventory, analytics, and AI assistant dashboard by Sailesh Pabbisetti.">
  <link rel="preconnect" href="https://images.unsplash.com">
  <link rel="stylesheet" href="assets/css/styles.css">
</head>
<body>
  <div class="app-shell">
    <aside class="sidebar">
      <a class="brand" href="#overview" aria-label="AutoFlow Intelligence home">
        <span class="brand-mark">AF</span>
        <span>
          <strong>AutoFlow</strong>
          <small>Intelligence</small>
        </span>
      </a>
      <nav class="nav-links" aria-label="Main navigation">
        <a href="#overview" class="active">Overview</a>
        <a href="#inventory">Inventory</a>
        <a href="#pipeline">Pipeline</a>
        <a href="#analytics">Analytics</a>
        <a href="#assistant">AI Copilot</a>
      </nav>
      <div class="operator-card">
        <span class="status-dot"></span>
        <p>Built by Sailesh Pabbisetti</p>
        <strong>Full Stack Developer | Data Analyst</strong>
      </div>
    </aside>

    <main class="workspace">
      <header class="hero" id="overview">
        <div class="hero-copy">
          <p class="eyebrow">Automotive operations platform</p>
          <h1>Inventory, sales leads, analytics, and AI follow-up in one professional dashboard.</h1>
          <p class="hero-text">A full-stack PHP and JavaScript project designed for dealership teams that need faster decisions, cleaner customer tracking, and data-driven sales workflows.</p>
          <div class="hero-actions">
            <a href="#inventory" class="button primary">View inventory</a>
            <a href="#assistant" class="button ghost">Open AI copilot</a>
          </div>
        </div>
        <section class="hero-panel" aria-label="Live operations snapshot">
          <div class="glass-header">
            <span>Live Operations</span>
            <strong id="targetProgress">Loading</strong>
          </div>
          <div class="speedometer" aria-hidden="true">
            <span></span>
          </div>
          <div class="mini-grid">
            <div><small>Available</small><strong id="availableCount">--</strong></div>
            <div><small>Reserved</small><strong id="reservedCount">--</strong></div>
            <div><small>Avg Price</small><strong id="averagePrice">--</strong></div>
          </div>
        </section>
      </header>

      <section class="kpi-grid" id="kpiGrid" aria-label="Key performance indicators"></section>

      <section class="section-heading" id="inventory">
        <div>
          <p class="eyebrow">Inventory intelligence</p>
          <h2>Vehicle catalog</h2>
        </div>
        <form class="filters" id="inventoryFilters">
          <input type="search" name="q" placeholder="Search brand, model, category">
          <select name="category" aria-label="Category">
            <option value="all">All categories</option>
            <option value="SUV">SUV</option>
            <option value="Sedan">Sedan</option>
            <option value="Compact">Compact</option>
            <option value="Electric">Electric</option>
          </select>
          <select name="fuel" aria-label="Fuel type">
            <option value="all">All fuel types</option>
            <option value="Diesel">Diesel</option>
            <option value="Petrol">Petrol</option>
            <option value="Hybrid">Hybrid</option>
            <option value="Electric">Electric</option>
          </select>
        </form>
      </section>

      <section class="vehicle-grid" id="vehicleGrid" aria-live="polite"></section>

      <section class="split-layout">
        <div class="panel" id="pipeline">
          <div class="panel-title">
            <div>
              <p class="eyebrow">CRM pipeline</p>
              <h2>Lead follow-up board</h2>
            </div>
            <select id="leadFilter" aria-label="Lead temperature filter">
              <option value="all">All leads</option>
              <option value="Hot">Hot</option>
              <option value="Warm">Warm</option>
              <option value="Cold">Cold</option>
            </select>
          </div>
          <div class="lead-table" id="leadTable"></div>
        </div>

        <div class="panel assistant-panel" id="assistant">
          <div class="panel-title">
            <div>
              <p class="eyebrow">AI automation</p>
              <h2>Sales copilot</h2>
            </div>
            <button class="icon-button" id="refreshAssistant" aria-label="Refresh recommendations">↻</button>
          </div>
          <p class="muted" id="assistantSummary">Analyzing live sales signals...</p>
          <div id="assistantList" class="assistant-list"></div>
        </div>
      </section>

      <section class="panel analytics-panel" id="analytics">
        <div class="panel-title">
          <div>
            <p class="eyebrow">Data analysis</p>
            <h2>Revenue performance</h2>
          </div>
          <span class="badge">JavaScript chart</span>
        </div>
        <div class="chart" id="revenueChart" aria-label="Revenue chart"></div>
      </section>
    </main>
  </div>

  <script src="assets/js/app.js" defer></script>
</body>
</html>

