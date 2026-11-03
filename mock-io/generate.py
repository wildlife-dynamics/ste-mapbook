"""Regenerate the synthetic mock-IO data in this folder.

Run from the repo root with any env that has geopandas and pyarrow:

    python mock-io/generate.py

It writes two files:

- the observations, with the same columns and dtypes as the example return
  shipped with `ecoscope.platform.tasks.io.get_subjectgroup_observations`, but
  describing one made-up collared elephant moving around Samburu and Buffalo
  Springs. Every name, ID and position is synthetic; the seed makes it
  reproducible.
- the seasonal windows `compute_seasons_from_ndvi` returns: Samburu's two rainy
  seasons in 2011, in the shape `ecoscope.analysis.seasons.seasonal_windows`
  builds from NDVI.
"""

import uuid
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

HERE = Path(__file__).parent
OBSERVATIONS_OUT = HERE / "get-subjectgroup-observations.example-return.parquet"
SEASONS_OUT = HERE / "compute-seasons-from-ndvi.example-return.parquet"
SEED = 20110101
SERVER = "https://mock.pamdas.org"

# The test cases' time range (2011), a full year so the NDVI-based seasonal
# windows have both wet and dry seasons to label.
START = pd.Timestamp("2011-01-01T00:00:00Z")
END = pd.Timestamp("2011-12-31T21:00:00Z")
FIX_INTERVAL = "3h"  # within the trajectory filter's 6 h max gap

# name, sex, home-range centre (lon, lat), home-range spread (degrees)
ELEPHANTS = [
    ("Mock Ewaso", "female", (37.53, 0.60), 0.05),
]


def _track(rng: np.random.Generator, centre, spread, n: int) -> np.ndarray:
    """A correlated random walk pulled back towards the home-range centre."""
    km_per_deg = 111.0
    pos = np.empty((n, 2))
    pos[0] = centre
    heading = rng.uniform(0, 2 * np.pi)
    for i in range(1, n):
        hour = (i * 3) % 24
        # Elephants move least in the midday heat, most at dusk and at night.
        activity = 0.4 if 10 <= hour <= 15 else 1.0
        step_km = min(rng.lognormal(mean=np.log(1.1), sigma=0.6) * activity, 4.5)
        heading += rng.normal(0, 0.7)
        drift = (np.asarray(centre) - pos[i - 1]) / spread  # stay near home
        move = np.array([np.cos(heading), np.sin(heading)]) + 0.35 * drift
        move /= np.linalg.norm(move)
        pos[i] = pos[i - 1] + move * step_km / km_per_deg
    return pos


def build() -> gpd.GeoDataFrame:
    rng = np.random.default_rng(SEED)
    times = pd.date_range(START, END, freq=FIX_INTERVAL)
    tenant = str(uuid.UUID(int=rng.integers(2**63)))
    frames = []
    for name, sex, centre, spread in ELEPHANTS:
        subject_id = str(uuid.UUID(int=rng.integers(2**63)))
        source_id = str(uuid.UUID(int=rng.integers(2**63)))
        pos = _track(rng, centre, spread, len(times))
        last_lon, last_lat = pos[-1]
        last_time = times[-1].isoformat()
        subject_created = pd.Timestamp("2010-12-01T10:00:00+03:00").as_unit("ns")
        n = len(times)
        ids = [str(uuid.UUID(int=int(x))) for x in rng.integers(2**63, size=n)]
        frames.append(
            pd.DataFrame(
                {
                    "id": ids,
                    "extra__id": ids,
                    "extra__location": [{"latitude": lat, "longitude": lon} for lon, lat in pos],
                    "extra__recorded_at": times,
                    "extra__created_at": times.shift(5, freq="min"),
                    "extra__exclusion_flags": 0.0,
                    "extra__das_tenant_id": tenant,
                    "extra__source": source_id,
                    "extra__subject_id": subject_id,
                    "geometry": [Point(lon, lat) for lon, lat in pos],
                    "extra__subject__content_type": "observations.subject",
                    "extra__subject__id": subject_id,
                    "extra__subject__name": name,
                    "extra__subject__subject_type": "wildlife",
                    "extra__subject__subject_subtype": "elephant",
                    "extra__subject__common_name": None,
                    "extra__subject__created_at": subject_created,
                    "extra__subject__updated_at": subject_created,
                    "extra__subject__is_active": True,
                    "extra__subject__user": None,
                    "extra__subject__tracks_available": True,
                    "extra__subject__image_url": "/static/elephant-black.svg",
                    "extra__subject__last_position_status": [
                        {"last_voice_call_start_at": None, "radio_state": "na", "radio_state_at": None}
                    ]
                    * n,
                    "extra__subject__last_position_date": times[-1],
                    "extra__subject__last_position": [
                        {
                            "geometry": {"coordinates": [last_lon, last_lat], "type": "Point"},
                            "properties": {
                                "DateTime": last_time,
                                "coordinateProperties": {"time": last_time},
                                "id": subject_id,
                                "image": f"{SERVER}/static/elephant-black.svg",
                                "last_voice_call_start_at": None,
                                "location_requested_at": None,
                                "radio_state": "na",
                                "radio_state_at": "1970-01-01T00:00:00+00:00",
                                "stroke": "#FFFF00",
                                "stroke-opacity": 1.0,
                                "stroke-width": 2,
                                "subject_subtype": "elephant",
                                "subject_type": "wildlife",
                                "title": name,
                            },
                            "type": "Feature",
                        }
                    ]
                    * n,
                    "extra__subject__device_status_properties": None,
                    "extra__subject__url": f"{SERVER}/api/v1.0/subject/{subject_id}",
                    "extra__subject__hex": "#ff0000",
                    "groupby_col": subject_id,
                    "fixtime": times,
                    "junk_status": False,
                    "extra__subject__sex": sex,
                }
            )
        )
    df = pd.concat(frames, ignore_index=True).sort_values(["fixtime", "extra__subject__name"], ignore_index=True)
    df["extra__subject__created_at"] = df["extra__subject__created_at"].dt.tz_convert("+03:00")
    df["extra__subject__updated_at"] = df["extra__subject__updated_at"].dt.tz_convert("+03:00")
    return gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326").set_index("id")


# Samburu has two rainy seasons: the long rains (Mar-May) and the short rains
# (late Oct-Dec). Labels match the spec's Dry/Wet colour mapping. Together the
# windows cover the whole test time range. create_seasonal_labels excludes a
# window's start, so the first one opens before the first fix (2011-01-01 00:00).
SEASONS = [
    ("2010-12-01", "2011-03-15", "Dry"),
    ("2011-03-15", "2011-06-01", "Wet"),
    ("2011-06-01", "2011-10-20", "Dry"),
    ("2011-10-20", "2012-01-01", "Wet"),
]


def build_seasons() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "start": pd.to_datetime([s for s, _, _ in SEASONS], utc=True).as_unit("ns"),
            "end": pd.to_datetime([e for _, e, _ in SEASONS], utc=True).as_unit("ns"),
            "season": [label for _, _, label in SEASONS],
        },
        index=pd.Index(range(1, len(SEASONS) + 1), name="unique_season"),
    )


if __name__ == "__main__":
    gdf = build()
    gdf.to_parquet(OBSERVATIONS_OUT)
    print(f"Wrote {len(gdf)} observations for {gdf['extra__subject__name'].nunique()} subjects to {OBSERVATIONS_OUT}")
    seasons = build_seasons()
    seasons.to_parquet(SEASONS_OUT)
    print(f"Wrote {len(seasons)} seasonal windows to {SEASONS_OUT}")
