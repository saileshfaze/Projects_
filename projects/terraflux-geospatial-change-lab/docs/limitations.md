# Realistic limitations and next steps

- **No sensor correction:** reflectance is assumed normalized and co-registered. Real multispectral acquisitions need atmospheric correction, cloud/shadow QA, sensor harmonization, reprojection and resampling.
- **Projection distortion:** EPSG:3857 is metric in coordinates but area-distorting. Reported square metres are projected, not geodesic surface area. Use equal-area projection for serious land-area reporting.
- **Rule-based screening:** NDVI/NBR thresholds are not a supervised classifier. Seasonal cycles, drought, crop harvest and illumination can mimic vegetation loss.
- **Simplified uncertainty:** block-bootstrap intervals describe map fraction variability under block resampling, not epistemic uncertainty or true detection accuracy.
- **Synthetic-only validation:** generated scenes have idealized clearing patches and do not establish real-world precision or recall.
- **Geometries:** exact pixel-cell MultiPolygons can be verbose and include adjacent, undissolved polygons. A production implementation should dissolve cells and simplify boundaries with topology checks.
- **Scalability:** the pipeline holds full rasters in memory and processes components in Python. Large scenes require chunking, distributed raster operations and tiled vectorization.
- **Service hardening:** no auth, quota, worker queue, distributed locks or observability stack; SQLite is suitable for local demonstrations only.

Next steps: GeoTIFF/COG ingestion, equal-area reprojection, shadow masks, real labeled datasets, STAC integration, streaming tiled inference, calibration curves and a documented evaluation protocol.
