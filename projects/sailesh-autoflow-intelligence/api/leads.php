<?php
declare(strict_types=1);

require __DIR__ . '/bootstrap.php';

$leads = read_json('leads.json');
$temperature = strtolower(trim($_GET['temperature'] ?? 'all'));

$filtered = array_values(array_filter($leads, function (array $lead) use ($temperature): bool {
    return $temperature === 'all' || strtolower($lead['temperature']) === $temperature;
}));

respond([
    'count' => count($filtered),
    'items' => $filtered,
]);

