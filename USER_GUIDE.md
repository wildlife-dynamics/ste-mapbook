# STE Mapbook Workflow — User Guide

This guide walks you through loading, configuring, and running the STE Mapbook Workflow, which generates a multi-section mapbook report for wildlife tracking data sourced from EarthRanger and Google Earth Engine.

---

## What it produces

- Six interactive map visualizations (movement tracks, speed, day/night, home range, mean speed raster, seasonal home range)
- A Word document mapbook (`.docx`) with a cover page and one section per subject
- An interactive widget dashboard

## Requirements

- Access to an **EarthRanger** instance with a configured data source
- Access to a **Google Earth Engine** project
- The `landDx` geodatabase (downloaded automatically from Dropbox by default — no local copy required)

---

## 1. Load the Workflow

In the workflow runner, add a new template using this repository's URL:

```
https://github.com/wildlife-dynamics/ste-mapbook.git
```

Once added, select **STE Mapbook Workflow** from the available templates list to load it.

---

## 2. Configure the Workflow

You'll be prompted to fill in the following parameters before running.

### Workflow Details

| Field | Description |
|-------|-------------|
| Workflow Name | A short name to identify this run |
| Workflow Description | Optional description |

### Data Source Connections

Both an **EarthRanger** connection and a **Google Earth Engine** connection are required for the workflow to run.

| Field | Description |
|-------|-------------|
| Connect to EarthRanger | Select (or create) the EarthRanger connection to pull observations from |
| Connect to Earth Engine | Select the Google Earth Engine project used for seasonal analysis |

### Basemap Layer

The **Configure basemap layers** step sets the background tile layer shared by all six maps. It's pre-filled with a sensible default, but the URL, opacity, and max zoom are editable if you want a different base layer.

| Field | Default |
|-------|---------|
| Tile URL | `ArcGIS World Hillshade` |
| Opacity | `1.0` (fully opaque) |
| Max Zoom | `20` |

### Analysis Time Range

| Field | Description |
|-------|-------------|
| Since | Start date/time of the analysis period |
| Until | End date/time of the analysis period |

> **Note:** Very short analysis periods (a few days or weeks) can cause the seasonal analysis step to fail with a Google Earth Engine `User memory limit exceeded` error. If you hit this, widen the **Since**/**Until** range — a window of two to three months or more gives Earth Engine enough NDVI history to compute season windows reliably.

### Previous Period Range

Defines the comparison period shown on the Movement Tracks map. In every mode, the comparison period's **end date** is fixed to your time range's start date (so the two periods never overlap) — only the start date calculation changes. Choose one of three modes:

| Mode | Description |
|------|-------------|
| **Preset** | Pick a common lookback: Same as current period, Previous month, Previous 3 months, Previous 6 months, or Previous year |
| **Calendar** | Manually pick the exact start date for the comparison period |
| **Custom** | Enter a Years / Months / Weeks / Days offset to count backward from your time range's start date (default: 1 month back) |

Default is **Preset → Same as current period**.

### Subject Group

| Field | Description | Default |
|-------|-------------|---------|
| Subject Group Name | The subject group in EarthRanger, picked from a drop-down of the subject groups on the chosen data source | `Elephants` |
| Include Subject Additional *(advanced)* | Whether to include the subject's free-form `additional` JSON metadata from EarthRanger. Applied to both the current and previous period observation fetches | `false` |

### Map Overlay

Choose the overlay layer to display on all maps.

| Option | Description | Default |
|--------|-------------|---------|
| **LandDx** | Protected area boundaries (community conservancies, national reserves, national parks), downloaded from a `.gpkg` URL or a local file | Pre-filled Dropbox URL |
| **EarthRanger Spatial Feature** | Fetches a named spatial feature set directly from your connected EarthRanger instance | — |

By default, **LandDx** is pre-selected with the download URL filled in — no action required unless you want to use an EarthRanger spatial feature instead.

### Trajectory Segment Filter

Removes GPS noise and unrealistic movements before trajectory analysis. Applied to both current and previous period trajectories.

| Field | Default | Description |
|-------|---------|-------------|
| Minimum Segment Length (m) | `0.001` | Discard segments shorter than this distance |
| Maximum Segment Length (m) | `5000` | Discard segments longer than this distance |
| Minimum Segment Duration (s) | `1` | Discard segments shorter than this duration |
| Maximum Segment Duration (s) | `21600` | Discard segments longer than this duration (6 hours) |
| Minimum Speed (km/h) | `0.01` | Discard segments below this average speed |
| Maximum Speed (km/h) | `9` | Discard segments above this average speed |

Adjust these values to suit the movement characteristics of your study species — overly tight bounds can filter out most of a subject's data.

### Mean Speed Raster

| Field | Default | Description |
|-------|---------|-------------|
| Step Length (m) | `2000`, or **Auto** | Cell size of the mean speed raster. Smaller values are more detailed but slower and larger; **Auto** uses the average distance between consecutive GPS fixes instead of a fixed value |

### Zoom to GDF Extent

| Field | Default | Description |
|-------|---------|-------------|
| Expansion Factor | `1.05` | Padding around the map boundary. `1.0` = tight fit, `1.2` = 20% padding |

### Generate Word Doc Report

Controls the mapbook `.docx` output.

| Field | Default | Description |
|-------|---------|-------------|
| Include Maps | Enabled | When enabled, all six interactive maps are converted to images and embedded in each subject's report section. Disabling it skips image generation and produces the report without map images |
| Report Logo | — | Appears on the mapbook cover page. Provide a URL to a PNG/JPG to download it automatically, or a local file path |

---

## 3. Run the Workflow

Once all parameters are configured, submit the workflow. The runner will:

1. Pull movement data from EarthRanger for the specified subject group and time range.
2. Filter trajectories using the segment filter settings.
3. Compute home ranges, speed rasters, and seasonal ranges using Google Earth Engine.
4. Generate all map visualizations and the Word mapbook.
5. Save all outputs to the directory specified by `ECOSCOPE_WORKFLOWS_RESULTS`.

### Output Files

All outputs are written to `$ECOSCOPE_WORKFLOWS_RESULTS/`:

| File | Description |
|------|-------------|
| `trajectories.geoparquet` | Current period trajectories |
| `previous_period_trajectories.geoparquet` | Previous period trajectories |
| `relocations.geoparquet` | Current period relocations |
| `previous_period_relocations.geoparquet` | Previous period relocations |
| `*.geoparquet` (ETD, MCP, seasonal) | Home range polygons per subject |
| `*_movement_tracks.html` | Interactive movement tracks map per subject |
| `*_speedmap.html` | Interactive speed map per subject |
| `*_day_night.html` | Interactive day/night map per subject |
| `*_homerange.html` | Interactive home range map per subject |
| `*_mean_speed_raster.html` | Interactive mean speed raster map per subject |
| `*_seasonal_home_range.html` | Interactive seasonal home range map per subject |
| `mapbook_context_page.docx` | Cover page document |
| `*.docx` (per subject) | Individual subject report sections |
| Merged mapbook `.docx` | Final combined Word report |

---

## More Help

- **Full documentation site:** [wildlife-dynamics.github.io/ste-mapbook](https://wildlife-dynamics.github.io/ste-mapbook/) — user guide, technical guide, and troubleshooting
- **Issues:** [github.com/wildlife-dynamics/ste-mapbook/issues](https://github.com/wildlife-dynamics/ste-mapbook/issues)
