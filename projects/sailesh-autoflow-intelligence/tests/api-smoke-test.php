<?php
declare(strict_types=1);

$files = [
    'vehicles.json' => ['id', 'brand', 'model', 'price', 'status'],
    'leads.json' => ['id', 'customerName', 'preferredVehicle', 'temperature', 'nextAction'],
    'targets.json' => ['month', 'target', 'actual', 'leads'],
];

foreach ($files as $file => $requiredKeys) {
    $path = dirname(__DIR__) . '/assets/data/' . $file;
    $decoded = json_decode((string) file_get_contents($path), true);

    if (!is_array($decoded) || count($decoded) === 0) {
        fwrite(STDERR, "Invalid seed data: {$file}\n");
        exit(1);
    }

    foreach ($requiredKeys as $key) {
        if (!array_key_exists($key, $decoded[0])) {
            fwrite(STDERR, "Missing {$key} in {$file}\n");
            exit(1);
        }
    }

    echo "OK {$file}\n";
}

echo "Seed data smoke test passed.\n";
