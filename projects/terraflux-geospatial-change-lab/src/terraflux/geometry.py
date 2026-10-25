"""Connected-component extraction and exact pixel-cell GeoJSON geometry."""
from collections import deque
import numpy as np


def components(mask: np.ndarray, minimum: int = 1) -> list[list[tuple[int, int]]]:
    if mask.ndim != 2:
        raise ValueError("mask must be 2D")
    visited = np.zeros_like(mask, dtype=bool)
    groups = []
    h, w = mask.shape
    for r in range(h):
        for c in range(w):
            if not mask[r, c] or visited[r, c]:
                continue
            queue = deque([(r, c)])
            visited[r, c] = True
            group = []
            while queue:
                y, x = queue.popleft()
                group.append((y, x))
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not visited[ny, nx]:
                            visited[ny, nx] = True
                            queue.append((ny, nx))
            if len(group) >= minimum:
                groups.append(sorted(group))
    return sorted(groups, key=lambda g: (-len(g), g[0]))


def cell_geometry(cells: list[tuple[int, int]], transform: tuple[float, ...]) -> dict:
    """MultiPolygon of horizontal pixel runs; no bounding-box area inflation."""
    x0, dx, _, y0, _, dy = transform
    by_row: dict[int, list[int]] = {}
    for row, col in cells:
        by_row.setdefault(row, []).append(col)
    polygons = []
    for row in sorted(by_row):
        cols = sorted(by_row[row])
        start = previous = cols[0]
        runs = []
        for col in cols[1:]:
            if col == previous + 1:
                previous = col
            else:
                runs.append((start, previous + 1))
                start = previous = col
        runs.append((start, previous + 1))
        for left, right in runs:
            xa, xb = x0 + left * dx, x0 + right * dx
            ya, yb = y0 + row * dy, y0 + (row + 1) * dy
            polygons.append([[[xa, ya], [xb, ya], [xb, yb], [xa, yb], [xa, ya]]])
    return {"type": "MultiPolygon", "coordinates": polygons}


def feature_collection(groups: list[list[tuple[int, int]]], transform: tuple[float, ...],
                       drops: np.ndarray) -> dict:
    pixel_area = abs(transform[1] * transform[5])
    features = []
    for index, group in enumerate(groups, 1):
        mean_drop = float(np.mean([drops[y, x] for y, x in group]))
        features.append({"type": "Feature", "id": index,
                         "geometry": cell_geometry(group, transform),
                         "properties": {"patch_id": index, "pixels": len(group),
                                        "area_m2": round(len(group) * pixel_area, 3),
                                        "mean_ndvi_drop": round(mean_drop, 4)}})
    return {"type": "FeatureCollection", "features": features,
            "crs": {"type": "name", "properties": {"name": "EPSG:3857"}}}
