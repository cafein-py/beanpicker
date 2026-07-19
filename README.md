# beanpicker

AOI-driven OSM and GTFS acquisition, validation and repair — companion to
[pyrosm](https://github.com/HTenkanen/pyrosm) and cafein. beanpicker selects
and prepares the raw beans (OSM and GTFS data) that cafein brews into routing
results.

**Status: early development.** Acquisition (Mobility Database catalog + OSM
extracts), GTFS validation, repair and cropping are in place, tied together by
the one-call `beanpicker.fetch` pipeline.

## Quick example

```python
import beanpicker

# One call: OSM extract + validated GTFS feeds for an area of interest.
result = beanpicker.fetch(helsinki_polygon)        # any shapely geometry,
                                                   # bbox tuple or place name
result.osm_pbf     # cropped OSM extract (path)
result.feeds       # downloaded, cropped and validated GTFS feeds (paths)
result.reports     # per-feed merged validation reports
result.skipped     # (feed id, reason) for anything left out

net = result.to_cafein()   # routable cafein.TransportNetwork
osm = result.to_pyrosm()   # pyrosm.OSM reader over the extract
```

`fetch` accepts `when="2026-09-01"` to pick the dataset versions covering a
service day (needs a free Mobility Database API token, passed as
`refresh_token=` or via the `MOBILITY_API_REFRESH_TOKEN` environment
variable), `modes=["rail", "tram"]` to keep only feeds serving given modes,
and `repair=True` to repair feeds before use. With a token, GTFS downloads
are catalogued dataset versions verified against catalog checksums; without
one, the latest hosted zips are fetched as-is — unverified moving targets.

### Lower-level access

Each pipeline stage is available on its own:

```python
db = beanpicker.MobilityDatabase()

feeds = db.search_feeds(aoi=helsinki_polygon)
dataset = db.dataset_for(feeds[0], when="2026-09-01")
path = db.download(dataset)                        # cached, checksum-verified
report = db.validation_report(dataset)             # hosted canonical-validator report

pbf = beanpicker.fetch_pbf(helsinki_polygon)       # cropped OSM extract
validation = beanpicker.validate_feed(path)        # canonical-code notices
beanpicker.repair_feed(path, "repaired.zip")       # gtfstidy-contract repair
beanpicker.crop_feed(path, "cropped.zip", aoi=helsinki_polygon)
```

## Installation

Not yet on PyPI. From source (requires a Rust toolchain):

```
pip install .
```

## License

MIT
