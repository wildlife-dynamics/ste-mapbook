# Mock-IO data

Synthetic example returns for the IO tasks, used by the `mock_io` test cases in
`test-cases.yaml` (see `.github/workflows/test.yml`, which points the
`WT_TASK_MOCK_IO__…` environment variables at these files).

| File | Mocks |
|---|---|
| `get-subjectgroup-observations.example-return.parquet` | `ecoscope.platform.tasks.io.get_subjectgroup_observations` |
| `compute-seasons-from-ndvi.example-return.parquet` | `ecoscope_workflows_ext_ste.tasks.io.compute_seasons_from_ndvi` |

## Observations

They have the same columns and types as the example return shipped with
`get_subjectgroup_observations`, but describe four made-up collared elephants
(two female, two male) instead of the generic ranger and helicopter subjects.
Every name, ID and position is made up: each track is a correlated random walk
around a home range in Samburu, Buffalo Springs, Kalama or Shaba, so the maps
overlap the LandDx protected areas.

Fixes are 3-hourly through 2011, matching the test cases' time range. Every
step passes the workflow's trajectory segment filter (≤ 5 km, ≤ 6 h, ≤ 9 km/h).

The same file is returned for both the current and the previous period.

## Seasonal windows

Four Dry/Wet windows covering 2011, following Samburu's two rainy seasons (long
rains Mar–May, short rains late Oct–Dec), instead of computing them from MODIS
NDVI on Earth Engine. Same shape as `ecoscope.analysis.seasons.seasonal_windows`
returns: `start`, `end` (UTC) and `season`, indexed by `unique_season`. Every
mock fix falls inside a window, and the labels match the spec's Dry/Wet colours.

`compute_seasons_from_ndvi` is only mocked once ext-ste registers it as an IO
task (`@register(tags=["io"])`); until then the workflow still calls Earth Engine
and this file is unused.

## Regenerating

Both files are seeded, so the output is reproducible. Run
`python mock-io/generate.py` from the repo root in an env with geopandas.
