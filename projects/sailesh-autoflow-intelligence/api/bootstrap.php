<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

function data_path(string $file): string
{
    return dirname(__DIR__) . '/assets/data/' . $file;
}

function read_json(string $file): array
{
    $path = data_path($file);
    if (!file_exists($path)) {
        http_response_code(500);
        echo json_encode(['error' => "Missing data file: {$file}"]);
        exit;
    }

    $content = file_get_contents($path);
    $decoded = json_decode($content ?: '[]', true);
    return is_array($decoded) ? $decoded : [];
}

function money(float|int $value): string
{
    return 'EUR ' . number_format((float) $value, 0, '.', ',');
}

function respond(array $payload): void
{
    echo json_encode($payload, JSON_PRETTY_PRINT);
    exit;
}

