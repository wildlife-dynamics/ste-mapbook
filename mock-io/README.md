# Mock-IO data

Synthetic example returns for the IO tasks, used by the `mock_io` test cases in
`test-cases.yaml` (see `.github/workflows/test.yml`, which points the
`WT_TASK_MOCK_IO__…` environment variables at these files).

They have the same columns and types as the example return shipped with
`get_subjectgroup_observations`, but describe four made-up collared elephants
(two female, two male) instead of the generic ranger and helicopter subjects.
Every name, ID and position is made up: each track is a correlated random walk
around a home range in Samburu, Buffalo Springs, Kalama or Shaba, so the maps
overlap the LandDx protected areas.

Fixes are 3-hourly through 2011, matching the test cases' time range, so the
NDVI seasonal windows have a full year to label. Every step passes the
workflow's trajectory segment filter (≤ 5 km, ≤ 6 h, ≤ 9 km/h).

The same file is returned for both the current and the previous period.

| File | Mocks |
|---|---|
| `get-subjectgroup-observations.example-return.parquet` | `ecoscope.platform.tasks.io.get_subjectgroup_observations` |

To regenerate it (seeded, so the output is reproducible), run
`python mock-io/generate.py` from the repo root in an env with geopandas.
