<?php
declare(strict_types=1);

require __DIR__ . '/bootstrap.php';

$vehicles = read_json('vehicles.json');
$query = strtolower(trim($_GET['q'] ?? ''));
$category = strtolower(trim($_GET['category'] ?? 'all'));
$fuel = strtolower(trim($_GET['fuel'] ?? 'all'));

$filtered = array_values(array_filter($vehicles, function (array $vehicle) use ($query, $category, $fuel): bool {
    $searchText = strtolower($vehicle['brand'] . ' ' . $vehicle['model'] . ' ' . $vehicle['category'] . ' ' . $vehicle['fuelType']);
    $matchesQuery = $query === '' || str_contains($searchText, $query);
    $matchesCategory = $category === 'all' || strtolower($vehicle['category']) === $category;
    $matchesFuel = $fuel === 'all' || strtolower($vehicle['fuelType']) === $fuel;
    return $matchesQuery && $matchesCategory && $matchesFuel;
}));

respond([
    'count' => count($filtered),
    'items' => $filtered,
]);

