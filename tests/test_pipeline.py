import zipfile

import httpx
import pytest

pytest.importorskip("beanpicker._core")

import beanpicker.catalog  # noqa: E402
import beanpicker.osm  # noqa: E402
from beanpicker.pipeline import fetch  # noqa: E402

GTFS = {
    "agency.txt": (
        "agency_id,agency_name,agency_url,agency_timezone\n"
        "hsl,HSL,https://hsl.fi,Europe/Helsinki\n"
    ),
    "stops.txt": (
        "stop_id,stop_name,stop_lat,stop_lon\n"
        "s1,Kamppi,60.169,24.931\ns2,Steissi,60.171,24.941\n"
    ),
    "routes.txt": "route_id,agency_id,route_short_name,route_type\nr1,hsl,1,3\n",
    "trips.txt": "route_id,service_id,trip_id\nr1,wk,t1\n",
    "stop_times.txt": (
        "trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
        "t1,08:00:00,08:00:00,s1,1\nt1,08:05:00,08:05:00,s2,2\n"
    ),
    "calendar.txt": (
        "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,"
        "start_date,end_date\nwk,1,1,1,1,1,0,0,20260101,20261231\n"
    ),
}

CSV_BODY = (
    "id,data_type,status,is_official,provider,"
    "location.country_code,location.subdivision_name,location.municipality,"
    "location.bounding_box.minimum_latitude,location.bounding_box.maximum_latitude,"
    "location.bounding_box.minimum_longitude,location.bounding_box.maximum_longitude,"
    "urls.direct_download,urls.latest,urls.license\n"
    "mdb-10,gtfs,active,True,HSL,FI,Uusimaa,Helsinki,59.9,60.6,24.2,25.6,"
    "https://example.com/hsl.zip,https://files.example.com/mdb-10/latest.zip,"
    "https://example.com/license\n"
)


@pytest.fixture
def pipeline_env(tmp_path, monkeypatch):
    import io as _io

    buffer = _io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, content in GTFS.items():
            archive.writestr(name, content)
    payload = buffer.getvalue()

    def handler(request):
        if request.url.path == "/feeds_v2.csv":
            return httpx.Response(200, text=CSV_BODY)
        if request.url.path == "/mdb-10/latest.zip":
            return httpx.Response(200, content=payload)
        return httpx.Response(404)

    monkeypatch.delenv("MOBILITY_API_REFRESH_TOKEN", raising=False)
    transport = httpx.MockTransport(handler)
    original = beanpicker.catalog.MobilityDatabase

    def patched(refresh_token=None, **kwargs):
        kwargs["transport"] = transport
        kwargs.setdefault("cache_dir", tmp_path)
        return original(refresh_token, **kwargs)

    monkeypatch.setattr("beanpicker.catalog.MobilityDatabase", patched)

    fake_pbf = tmp_path / "aoi.osm.pbf"
    fake_pbf.write_bytes(b"\x00fake")
    monkeypatch.setattr("beanpicker.osm._fetch.fetch_pbf", lambda *a, **k: fake_pbf)
    monkeypatch.setattr("beanpicker.osm.fetch_pbf", lambda *a, **k: fake_pbf)
    return tmp_path, fake_pbf


def test_fetch_end_to_end(pipeline_env):
    tmp_path, fake_pbf = pipeline_env
    with pytest.warns(UserWarning):
        result = fetch(
            (24.6, 60.1, 25.2, 60.4),
            directory=tmp_path,
            reference_date="20260601",
        )
    assert result.osm_pbf == fake_pbf
    assert len(result.feeds) == 1
    assert "-cropped-" in result.feeds[0].name
    assert result.feeds[0].suffix == ".zip"
    (report,) = result.reports
    assert report["summary"]["counts"]["errors"] == 0
    assert result.skipped == []
    assert result.repairs == [[]]
    pbf, feeds = result
    assert pbf == fake_pbf and feeds == result.feeds


def test_fetch_when_without_token_warns(pipeline_env):
    tmp_path, _ = pipeline_env
    with pytest.warns(UserWarning) as caught:
        result = fetch(
            (24.6, 60.1, 25.2, 60.4),
            when="2026-06-01",
            directory=tmp_path,
        )
    assert any("cannot select historical" in str(w.message) for w in caught)
    assert len(result.feeds) == 1


def test_fetch_rejects_unknown_mode(pipeline_env):
    tmp_path, _ = pipeline_env
    with pytest.raises(ValueError, match="unknown modes"):
        fetch((24.6, 60.1, 25.2, 60.4), modes=["hovercraft"], directory=tmp_path)


def test_fetch_mode_accepts_bare_string(pipeline_env):
    tmp_path, _ = pipeline_env
    with pytest.warns(UserWarning):
        result = fetch(
            (24.6, 60.1, 25.2, 60.4),
            modes="bus",
            directory=tmp_path,
            reference_date="20260601",
        )
    assert len(result.feeds) == 1


def test_fetch_mode_filter(pipeline_env):
    tmp_path, _ = pipeline_env
    with pytest.warns(UserWarning):
        result = fetch(
            (24.6, 60.1, 25.2, 60.4),
            modes=["ferry"],
            directory=tmp_path,
            reference_date="20260601",
        )
    assert result.feeds == []
    assert len(result.skipped) == 1
    assert "ferry" in result.skipped[0][1]


def test_fetch_place_name_aoi(pipeline_env, monkeypatch):
    from shapely.geometry import box

    tmp_path, fake_pbf = pipeline_env
    monkeypatch.setattr(
        "beanpicker.osm._fetch._as_geometry",
        lambda aoi: box(24.6, 60.1, 25.2, 60.4),
    )
    with pytest.warns(UserWarning):
        result = fetch("Helsinki", directory=tmp_path, reference_date="20260601")
    assert len(result.feeds) == 1


def test_fetch_skips_day_outside_service_window(pipeline_env):
    tmp_path, _ = pipeline_env
    with pytest.warns(UserWarning):
        result = fetch(
            (24.6, 60.1, 25.2, 60.4),
            when="2027-06-01",
            directory=tmp_path,
        )
    assert result.feeds == []
    ((feed_id, reason),) = result.skipped
    assert feed_id == "mdb-10"
    assert "no service on the requested day" in reason
    assert "20260101..20261231" in reason


def test_feed_modes_undeterminable(tmp_path):
    from beanpicker.pipeline._fetch import _feed_modes

    not_a_zip = tmp_path / "feed.zip"
    not_a_zip.write_bytes(b"not a zip archive")
    assert _feed_modes(not_a_zip) is None

    no_routes = tmp_path / "noroutes.zip"
    with zipfile.ZipFile(no_routes, "w") as archive:
        archive.writestr("agency.txt", "agency_id\n")
    assert _feed_modes(no_routes) is None


def test_mode_type_extended_blocks():
    from beanpicker.pipeline._fetch import _MODE_TYPES

    assert 300 in _MODE_TYPES["rail"]
    assert 100 in _MODE_TYPES["rail"]
    assert {400, 500, 600, 12} <= _MODE_TYPES["subway"]
    assert {200, 700, 800, 11} <= _MODE_TYPES["bus"]
    assert {900, 906, 5} <= _MODE_TYPES["tram"]
    assert {1000, 1200} <= _MODE_TYPES["ferry"]


def test_rank_prefers_official_active_specific():
    from beanpicker.catalog import Feed
    from beanpicker.pipeline._fetch import _rank

    def make(feed_id, official, status, box_deg=None):
        raw = {}
        if box_deg is not None:
            raw["latest_dataset"] = {
                "bounding_box": {
                    "minimum_longitude": 0.0,
                    "maximum_longitude": box_deg,
                    "minimum_latitude": 0.0,
                    "maximum_latitude": box_deg,
                }
            }
        return Feed(
            id=feed_id,
            provider=None,
            status=status,
            official=official,
            producer_url=None,
            license_url=None,
            latest_dataset_url=None,
            locations=(),
            raw=raw,
        )

    national = make("mdb-1", True, "active", box_deg=10.0)
    regional = make("mdb-2", True, "active", box_deg=1.0)
    unofficial = make("mdb-3", False, "active", box_deg=0.5)
    inactive = make("mdb-4", True, "inactive", box_deg=0.5)
    unknown_extent = make("mdb-5", True, "active")

    ordered = sorted(
        [national, unofficial, unknown_extent, inactive, regional], key=_rank
    )
    assert [f.id for f in ordered] == [
        "mdb-2",  # official, active, most specific
        "mdb-1",  # official, active, larger extent
        "mdb-5",  # official, active, unknown extent
        "mdb-4",  # official but inactive
        "mdb-3",  # unofficial
    ]
