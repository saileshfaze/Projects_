# Algorithm notes

## Spectral evidence

`NDVI = (NIR - red) / (NIR + red)` and `NBR = (NIR - SWIR) / (NIR + SWIR)`.

For clear pixels, the rule is:

- baseline NDVI ≥ 0.25;
- NDVI_before − NDVI_after ≥ 0.20;
- NBR_before − NBR_after ≥ 0.15.

Thresholds are configurable. The intersection reduces some false positives but cannot distinguish all land-cover changes from illumination, phenology, soil moisture, fires or sensor effects.

## Patch topology

Eight-neighbour connectivity merges diagonal touching pixels. Features are ordered by descending pixel count, then by first row/column. A feature is a MultiPolygon composed of maximal horizontal pixel runs, each represented by a rectangle. This exactly covers the selected cells, but adjacent rectangles are not dissolved into topologically simplified polygons.

## Spatial block bootstrap

Partition the valid raster into blocks, sample block indices with replacement, sum changed and valid counts, then calculate changed/valid fraction for each replicate. Return 2.5th and 97.5th percentiles. With few blocks, large clouds, spatial nonstationarity or systematic threshold error, this interval may be misleading. It is *not* a ground-truth accuracy interval.

## Complexity

Spectral operations are O(HW). Connected-component search is O(HW) with 8 neighbours per visited cell. Bootstrap is O(B·S) for B blocks and S samples. GeoJSON size is proportional to the number of horizontal pixel runs, which can be large for fragmented maps.
