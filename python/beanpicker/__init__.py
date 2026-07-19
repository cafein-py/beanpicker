"""AOI-driven OSM and GTFS acquisition, validation and repair."""

__all__ = [
    "Dataset",
    "Feed",
    "MobilityDatabase",
    "exceptions",
    "crop_feed",
    "fetch_pbf",
    "gtfs",
    "osm",
    "repair",
    "repair_feed",
    "report",
    "validate",
    "validate_feed",
    "__version__",
]


def __getattr__(name):
    if name in ("Dataset", "Feed", "MobilityDatabase"):
        from beanpicker import catalog

        return getattr(catalog, name)
    if name == "fetch_pbf":
        from beanpicker.osm import fetch_pbf

        return fetch_pbf
    if name == "crop_feed":
        from beanpicker.gtfs import crop_feed

        return crop_feed
    if name == "repair_feed":
        from beanpicker.repair import repair_feed

        return repair_feed
    if name == "validate_feed":
        from beanpicker.validate import validate_feed

        return validate_feed
    if name in ("exceptions", "gtfs", "osm", "repair", "report", "validate"):
        import importlib

        return importlib.import_module(f"beanpicker.{name}")
    if name == "__version__":
        from beanpicker._core import __version__

        return __version__
    raise AttributeError(f"module 'beanpicker' has no attribute {name!r}")
