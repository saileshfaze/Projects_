<?php
declare(strict_types=1);

require __DIR__ . '/bootstrap.php';

$vehicles = read_json('vehicles.json');
$leads = read_json('leads.json');

usort($vehicles, fn(array $a, array $b): int => $b['daysInStock'] <=> $a['daysInStock']);
$oldestVehicle = $vehicles[0] ?? null;
$hotLeads = array_values(array_filter($leads, fn(array $lead): bool => $lead['temperature'] === 'Hot'));
$reserved = array_values(array_filter($vehicles, fn(array $vehicle): bool => $vehicle['status'] === 'Reserved'));

$recommendations = [];

if ($oldestVehicle) {
    $recommendations[] = [
        'title' => 'Launch targeted campaign',
        'detail' => "Promote {$oldestVehicle['brand']} {$oldestVehicle['model']} because it has been in stock for {$oldestVehicle['daysInStock']} days.",
        'impact' => 'Reduce aging inventory and improve cash rotation',
    ];
}

foreach ($hotLeads as $lead) {
    $recommendations[] = [
        'title' => 'Prioritize hot lead follow-up',
        'detail' => "{$lead['customerName']} is ready for {$lead['preferredVehicle']}. Next action: {$lead['nextAction']}.",
        'impact' => 'Improve close rate with same-day action',
    ];
}

if ($reserved) {
    $vehicle = $reserved[0];
    $recommendations[] = [
        'title' => 'Protect reserved deal',
        'detail' => "Confirm documents and payment timing for {$vehicle['brand']} {$vehicle['model']}.",
        'impact' => 'Avoid reservation drop-off',
    ];
}

respond([
    'assistantName' => 'AutoFlow AI Sales Copilot',
    'summary' => 'Generated operational recommendations from inventory age, lead temperature, and deal status.',
    'recommendations' => array_slice($recommendations, 0, 5),
]);

