<?php
declare(strict_types=1);

require __DIR__ . '/bootstrap.php';

$vehicles = read_json('vehicles.json');
$leads = read_json('leads.json');
$targets = read_json('targets.json');

$available = array_filter($vehicles, fn(array $vehicle): bool => $vehicle['status'] === 'Available');
$reserved = array_filter($vehicles, fn(array $vehicle): bool => $vehicle['status'] === 'Reserved');
$hotLeads = array_filter($leads, fn(array $lead): bool => $lead['temperature'] === 'Hot');
$inventoryValue = array_sum(array_column($vehicles, 'price'));
$projectedMargin = array_sum(array_column($vehicles, 'margin'));
$latest = end($targets) ?: ['actual' => 0, 'target' => 1];
$targetProgress = round(($latest['actual'] / max(1, $latest['target'])) * 100, 1);

respond([
    'kpis' => [
        ['label' => 'Inventory Value', 'value' => money($inventoryValue), 'trend' => '+12.4%', 'tone' => 'green'],
        ['label' => 'Projected Margin', 'value' => money($projectedMargin), 'trend' => '+8.7%', 'tone' => 'blue'],
        ['label' => 'Hot Leads', 'value' => (string) count($hotLeads), 'trend' => '+18%', 'tone' => 'orange'],
        ['label' => 'Target Progress', 'value' => $targetProgress . '%', 'trend' => 'June', 'tone' => 'violet'],
    ],
    'inventory' => [
        'total' => count($vehicles),
        'available' => count($available),
        'reserved' => count($reserved),
        'averagePrice' => money($inventoryValue / max(1, count($vehicles))),
    ],
    'targets' => $targets,
]);

