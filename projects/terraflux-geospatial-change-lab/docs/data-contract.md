# Data contract

A dataset is a directory under `TERRAFLUX_DATA_ROOT`, named with a lowercase slug. Files: `before.npz`, `after.npz`, optional `truth.npy` and `manifest.json`. `np.load(..., allow_pickle=False)` is used. Both NPZ archives must contain exactly `red`, `nir`, `swir`, `cloud`, `scene_id`, `acquired_at`, `transform`, `crs`.

Each reflectance band is a finite 2D array of floats in `[0,1]`; `cloud` is a boolean 2D array of identical shape. Timestamps are ISO-8601 strings. The affine tuple is `(x_origin, pixel_width, 0, y_origin, 0, negative_pixel_height)`. CRS is exactly `EPSG:3857`. No implicit alignment, projection, nodata substitution, or radiometric calibration is performed.

Output JSON contains schema version, scene identifiers, acquisition times, settings, summary and GeoJSON. Areas are EPSG:3857 projected square metres. GeoJSON contains a legacy `crs` metadata object to make the non-WGS84 coordinate reference explicit; many GeoJSON consumers assume WGS84 regardless and will need explicit conversion.

The synthetic dataset is generated from a fixed seed and contains artificial clearing regions and clouds. It is not remotely sensed imagery.
